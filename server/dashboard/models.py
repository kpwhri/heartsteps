from datetime import date
from datetime import timedelta

from django.db import models
from django.utils import timezone

from adherence_messages.models import AdherenceMetric
from adherence_messages.models import AdherenceMessage
from adherence_messages.services import AdherenceAppInstallMessageService
from adherence_messages.services import AdherenceFitbitUpdatedService
from anti_sedentary.models import AntiSedentaryDecision
from activity_surveys.models import ActivitySurvey
from activity_surveys.models import Decision as ActivitySurveyDecision
from activity_surveys.models import Configuration as ActivitySurveyConfiguration
from burst_periods.models import Configuration as BurstPeriodConfiguration
from contact.models import ContactInformation
from days.services import DayService
from fitbit_activities.models import FitbitActivity
from fitbit_activities.models import FitbitActivitySummary
from fitbit_activities.services import FitbitActivityService
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from fitbit_api.services import FitbitService
from page_views.models import PageView
from page_views.models import PageViewSummary
from participants.models import Participant
from randomization.models import UnavailableReason
from sms_messages.models import Contact as SMSContact
from sms_messages.models import Message as SMSMessage
from walking_suggestions.models import WalkingSuggestionDecision
from walking_suggestion_surveys.models import Configuration as WalkingSuggestionSurveyConfiguration
from watch_app.models import StepCount as WatchAppStepCount
from watch_app.models import WatchInstall

from anti_sedentary.models import Configuration as AntiSedentaryConfiguration
from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from morning_messages.models import Configuration as MorningMessageConfiguration
from morning_messages.models import MorningMessage
from morning_messages.models import MorningMessageSurvey
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration

class AdherenceAppInstallDashboard(AdherenceAppInstallMessageService):

    def __init__(self, user=None):
        self._user = user

class InterventionSummary:
    
    def __init__(
            self,
            availability,
            decisions,
            messages_sent,
            unavailable_reasons
            ):
        self.availability = availability
        self.decisions = decisions
        self.messages_sent = messages_sent
        self.unavailable_reasons = unavailable_reasons
    
class InterventionSummaryManager(models.Manager):

    def get_intervention_decisions(self, model, users, start, end):
        query = model.objects.filter(
            user__in = users,
            time__gte = start,
            time__lte = end,
            test = False
        )
        return query.all()

    def get_walking_suggestions(self, users, start, end):
        return self.get_intervention_decisions(
            model = WalkingSuggestionDecision,
            users = users,
            start = start,
            end = end
        )

    def get_anti_sedentary_decisions(self, users, start, end):
        return self.get_intervention_decisions(
            model = AntiSedentaryDecision,
            users = users,
            start = start,
            end = end
        )

    def count_unavailable_reasons(self, decisions):
        unavailable_reasons = {}
        query = UnavailableReason.objects.filter(
            decision__in = decisions
        )
        for _reason in query.all():
            if _reason.reason not in unavailable_reasons:
                unavailable_reasons[_reason.reason] = 0
            unavailable_reasons[_reason.reason] += 1
        return unavailable_reasons

    def list_unavailable_reasons(self, decisions):
        counts = self.count_unavailable_reasons(decisions)
        decisions_total = len(decisions)
        unavailable_reasons = []
        for reason, name in UnavailableReason.CHOICES:
            count = 0
            percentage = 0
            if reason in counts:
                count = counts[reason]
            if decisions_total:
                percentage = count/decisions_total
            unavailable_reasons.append({
                'name': name,
                'reason': reason,
                'count': count,
                'percentage': percentage
            })
        unavailable_reasons.sort(key = lambda x: (1-x['percentage'], x['name']))
        return unavailable_reasons

    def filter_decisions(self, start, end, decisions):
        _decisions = []
        for decision in decisions:
            if decision.time >= start and decision.time <= end:
                _decisions.append(decision)
        return _decisions

    def summarize_interventions(self, users, start, end, decisions):
        total_decisions = 0
        available_decisions = 0
        messages_sent = 0
        decisions = self.filter_decisions(start, end, decisions)
        for decision in decisions:
            total_decisions += 1
            if decision.treated:
                messages_sent += 1
            if decision.available:
                available_decisions += 1
        availability = 0
        if total_decisions:
            availability = available_decisions/total_decisions

        return InterventionSummary(
            availability = availability,
            decisions = total_decisions,
            messages_sent = messages_sent,
            unavailable_reasons = self.list_unavailable_reasons(decisions)
        )

    def summarize_anti_sedentary_suggestions(
            self,
            users,
            start,
            end,
            decisions = None
        ):
        if not decisions:
            decisions = self.get_anti_sedentary_decisions(
                users = users,
                start = start,
                end = end
            )
        return self.summarize_interventions(
            users = users,
            start = start,
            end = end,
            decisions = decisions
        )        

    def summarize_walking_suggestions(self, users, start, end, decisions=None):
        if not decisions:
            decisions = self.get_walking_suggestions(
                users = users,
                start = start,
                end = end
            )
        return self.summarize_interventions(
            users = users,
            start = start,
            end = end,
            decisions = decisions
        )

class WatchAppSummary:

    def __init__(
            self,
            seconds_available,
            total_seconds
        ):
        self.seconds_available = seconds_available
        self.total_seconds = total_seconds

    @property
    def availability(self):
        if not self.total_seconds:
            return 0
        return self.seconds_available/self.total_seconds

    @property
    def hours_available(self):
        return self.seconds_available/3600

class WatchAppSummaryManager(models.Manager):

    def get_step_counts(self, users, start, end):
        step_counts = []
        query = WatchAppStepCount.objects.filter(
            user__in = users,
            start__gte = start,
            end__lte = end
        )
        return query.all()

    def __get_time_range(self, time_range):
        if time_range not in self.TIME_RANGES:
            raise RuntimeError('time range not found')
        else:
            service = DayService(user = self.user)
            today = service.get_current_date()
            start_date = today - timedelta(days=time_range.offset)
            return [
                service.get_start_of_day(start_date),
                service.get_end_of_day(today)
            ]

    def get_randomization_decisions(self, model, time_range):
        query = model.objects.filter(
            user = self.user,
            time__range = self.__get_time_range(time_range),
            test = False
        )
        for step_count in query.all():
            if step_count.end <= step_count.created:
                step_counts.append(step_count)
        return step_counts

    def get_user_timezone(self, user, dt):
        if not self._user_timezones:
            self._user_timezones = {}
        if user.username not in self._user_timezones:
            service = DayService(user = user)


    def summary(self, users, start, end):
        seconds_available = 0
        step_counts = self.get_step_counts(users, start, end)
        for count in step_counts:
            duration = count.end - count.start
            seconds_available += duration.seconds

        difference = end - start
        total_seconds = difference.days * 24 * 60 * 60 + difference.seconds
        return WatchAppSummary(
            seconds_available = seconds_available,
            total_seconds = total_seconds
        )

class DashboardParticipantQuerySet(models.QuerySet):

    def prefetch_burst_periods(self):
        return self

    def _prefetch_related_objects(self):
        lookup_functions = {
            'contact_information': self._fetch_contact_information,
            'page_views': self._fetch_page_views,
            'fitbit_account': self._fetch_fitbit_account,
            'walking_suggestion_survey_summary': self._fetch_walking_suggestion_survey_summary
        }
        updated_lookups = ()
        secondary_lookups = ()
        for lookup in self._prefetch_related_lookups:
            if lookup in lookup_functions.keys():
                secondary_lookups = secondary_lookups + (lookup, )
                continue
            updated_lookups = updated_lookups + (lookup, )
        self._prefetch_related_lookups = updated_lookups
        super()._prefetch_related_objects()
        for lookup in secondary_lookups:
            lookup_functions[lookup]()

    def prefetch_walking_suggestion_survey_summary():
        return self.prefetch_related('walking_suggestion_survey_summary')

    def _fetch_walking_suggestion_survey_summary(self):
        users = [p.user for p in self._result_cache if p.user]
        configurations = load_walking_suggestion_survey_summarys(users)
        configurations_by_username = {}
        for configuration in configurations:
            configurations_by_username[configuration.user.username] = configuration
        for participant in self._result_cache:
            if participant.user and participant.user.username in configurations_by_username:
                participant._walking_suggestion_survey_configuration = configurations_by_username[participant.user.username]
            else:
                p._walking_suggestion_survey_configuration = None

    def prefetch_contact_information(self):
        return self.prefetch_related('contact_information')

    def _fetch_contact_information(self):
        user_ids = [p.user.id for p in self._result_cache if p.user]
        contact_information_by_user_id = {}
        contact_information_query = ContactInformation.objects.filter(
            user_id__in = user_ids
        ).all()
        for contact_information in contact_information_query:
            contact_information_by_user_id[contact_information.user_id] = contact_information
        for _participant in self._result_cache:
            if _participant.user and _participant.user.id in contact_information_by_user_id:
                _participant._contact_information = contact_information_by_user_id[_participant.user.id]

    def prefetch_page_views(self):
        return self.prefetch_related('page_views')

    def _fetch_page_views(self):
        users = [p.user for p in self._result_cache if p.user]
        page_view_summary_by_user_id = {}
        page_view_summaries = PageViewSummary.objects.filter(user__in=users) \
        .prefetch_related('last_page_view') \
        .prefetch_related('first_page_view') \
        .all()
        for summary in page_view_summaries:
            page_view_summary_by_user_id[summary.user_id] = summary
        for participant in self._result_cache:
            if participant.user and participant.user.id in page_view_summary_by_user_id:
                summary = page_view_summary_by_user_id[participant.user.id]
                participant._first_page_view = summary.first_page_view
                participant._last_page_view = summary.last_page_view

    def prefetch_fitbit_account(self):
        return self.prefetch_related('fitbit_account')
    
    def _fetch_fitbit_account(self):
        user_ids = [p.user.id for p in self._result_cache if p.user]
        fitbit_account_id_by_user_id = {}
        fitbit_account_users = FitbitAccountUser.objects.filter(
            user_id__in = user_ids
        ).all()
        for account_user in fitbit_account_users:
            fitbit_account_id_by_user_id[account_user.user_id] = account_user.account_id
        account_ids = fitbit_account_id_by_user_id.values()
        fitbit_accounts = FitbitAccount.objects.filter(uuid__in=account_ids) \
        .prefetch_summary() \
        .all()
        fitbit_account_by_id = {}
        for fitbit_account in fitbit_accounts:
            fitbit_account_by_id[fitbit_account.uuid] = fitbit_account
        for participant in self._result_cache:
            if participant.user and participant.user.id in fitbit_account_id_by_user_id and fitbit_account_id_by_user_id[participant.user.id] in fitbit_account_by_id:
                participant._fitbit_account = fitbit_account_by_id[fitbit_account_id_by_user_id[participant.user.id]]
            else:
                participant._fitbit_account = None
        activity_summaries_by_account_id = {}
        for summary in FitbitActivitySummary.objects.filter(account_id__in=account_ids).all():
            activity_summaries_by_account_id[summary.account_id] = summary
        for participant in self._result_cache:
            if participant.user and participant.user.id in fitbit_account_id_by_user_id:
                account_id = fitbit_account_id_by_user_id[participant.user.id]
                if account_id in activity_summaries_by_account_id:
                    participant._fitbit_activity_summary = activity_summaries_by_account_id[fitbit_account_id_by_user_id[participant.user.id]]

class DashboardParticipant(Participant):

    summaries = InterventionSummaryManager()
    watch_app_step_counts = WatchAppSummaryManager()

    objects = DashboardParticipantQuerySet.as_manager()

    class Meta:
        proxy = True

    @property
    def study_start(self):
        return self.study_start_date

    @property
    def study_end(self):
        if self.study_length:
            return self.study_start_date + timedelta(days=self.study_length)
        else:
            return None

    @property
    def contact_information(self):
        if not hasattr(self, '_contact_information'):
            self._contact_information = self.get_contact_information()
        return self._contact_information

    def get_contact_information(self):
        try:
            return ContactInformation.objects.get(user=self.user)
        except ContactInformation.DoesNotExist:
            return None

    @property
    def phone_number(self):
        if self.contact_information:
            return self.contact_information.phone
        else:
            return None
    
    @property
    def fitbit_activity_summary(self):
        if not hasattr(self, '_fitbit_activity_summary'):
            self._fitbit_activity_summary = None
        return self._fitbit_activity_summary

    @property
    def fitbit_days_worn(self):
        if self.fitbit_activity_summary:
            return self.fitbit_activity_summary.days_worn
        else:
            return None

    @property
    def fitbit_account(self):
        if not hasattr(self, '_fitbit_account'):
            self._fitbit_account = self.get_fitbit_account()
        return self._fitbit_account

    def get_fitbit_account(self):
        if self.user:
            try:
                return FitbitAccountUser.objects.prefetch_related('account') \
                .get(user=self.user) \
                .account
            except FitbitAccountUser.DoesNotExist:
                pass
        return None

    @property
    def fitbit_authorized(self):
        if self.fitbit_account:
            service = FitbitService(account=self.fitbit_account)
            return service.is_authorized()
        return False

    @property
    def fitbit_first_updated(self):
        if self.fitbit_account:
            return self.fitbit_account.first_updated
        return None

    @property
    def fitbit_last_updated(self):
        if self.fitbit_account:
            return self.fitbit_account.last_updated
        return None

    @property
    def first_page_view(self):
        if hasattr(self, '_first_page_view') and self._first_page_view:
            return self._first_page_view.time
        return None

    @property
    def last_page_view(self):
        if hasattr(self, '_last_page_view') and self._last_page_view:
            return self._last_page_view.time
        return None

    @property
    def current_app_version(self):
        if hasattr(self, '_last_page_view') and self._last_page_view:
            return self._last_page_view.version
        return None

    @property
    def current_app_platform(self):
        if hasattr(self, '_last_page_view') and self._last_page_view:
            return self._last_page_view.platform
        return None

    @property
    def walking_suggestion_service_initialized_date(self):
        if not self.user:
            return None
        try:
            configuration = WalkingSuggestionConfiguration.objects.get(user=self.user)
            return configuration.service_initialized_date
        except WalkingSuggestionConfiguration.DoesNotExist:
            return None

    def adherence_status(self):
        statuses = []
        for category, title in AdherenceMetric.ADHERENCE_METRIC_CHOICES:
            metric = AdherenceMetric.objects.order_by('date').filter(
                user = self.user,
                category = category,
                value = True
            ).last()
            number_days = None
            if metric:
                diff = date.today() - metric.date
                number_days = diff.days
            statuses.append({
                'title': title,
                'days': number_days
            })
        return statuses

    def recent_adherence_messages(self):
        message_count = AdherenceMessage.objects.filter(
            user = self.user,
            created__gte = timezone.now() - timedelta(days=7)
        ).count()
        return message_count

    def get_adherence_during(self, start, end):
        if not self.user:
            return []
        metrics = {}
        adherence_metrics = AdherenceMetric.objects.filter(
            user = self.user,
            date__range = [start, end]
        ).all()
        for metric in adherence_metrics:
            if metric.date not in metrics:
                 metrics[metric.date] = {}
            metrics[metric.date][metric.category] = metric.value

        messages = {}
        day_service = DayService(user=self.user)
        adherence_messages = AdherenceMessage.objects.filter(
            user = self.user,
            created__range = [
                day_service.get_start_of_day(start),
                day_service.get_end_of_day(end)
            ]
        ).all()
        for message in adherence_messages:
            message_date = day_service.get_date(message.created)
            if message_date not in messages:
                messages[message_date] = []
            messages[message_date].append({
                'category': message.category,
                'body': message.body
            })
        
        summaries = []
        _dates = [end - timedelta(days=offset) for offset in range((end-start).days + 1)]
        for _date in _dates:
            _metrics = {}
            if _date in metrics:
                _metrics = metrics[_date]
            _messages = []
            if _date in messages:
                _messages = messages[_date]
            summaries.append({
                'date': _date,
                'metrics': _metrics,
                'messages': _messages
            })
        return summaries

    def is_enabled(self):
        if not self.user:
            return False
        configurations = [
            self.walking_suggestions_enabled,
            self.anti_sedentary_suggestions_enabled,
            self.morning_messages_enabled
        ]
        if True in configurations:
            return True
        else:
            return False

    def _is_configuration_enabled(self, model, keyname):
        if hasattr(self, keyname):
            return getattr(self, keyname)
        if not self.user:
            setattr(self, keyname, False)
        else:
            try:
                configuration = model.objects.get(user = self.user)
                setattr(self, keyname, configuration.enabled)
            except model.DoesNotExist:
                setattr(self, keyname, False)        
        return getattr(self, keyname)
        

    @property
    def walking_suggestions_enabled(self):
        return self._is_configuration_enabled(
            model = WalkingSuggestionConfiguration,
            keyname = '_walking_suggestions_enabled'
        )

    def get_last_walking_suggestion(self):
        if not self.user:
            return None
        return WalkingSuggestionDecision.objects.filter(
            user = self.user,
            test = False,
            treated = True
        ).order_by('time').last()

    @property
    def last_walking_suggestion(self):
        if not hasattr(self, '_last_walking_suggestion'):
            setattr(self, '_last_walking_suggestion', self.get_last_walking_suggestion())
        return getattr(self, '_last_walking_suggestion')
    
    @property
    def last_walking_suggestion_datetime(self):
        if self.last_walking_suggestion:
            return self.last_walking_suggestion.time
        else:
            return None

    @property
    def anti_sedentary_suggestions_enabled(self):
        return self._is_configuration_enabled(
            model = AntiSedentaryConfiguration,
            keyname = '_anti_sedentary_enabled'
        )

    def get_last_anti_sedentary_suggestion(self):
        if not self.user:
            return None
        return AntiSedentaryDecision.objects.filter(
            user = self.user,
            test = False,
            treated = True
        ).order_by('time').last()

    @property
    def last_anti_sedentary_suggestion(self):
        if not hasattr(self, '_last_anti_sedentary_suggestion'):
            setattr(self, '_last_anti_sedentary_suggestion', self.get_last_anti_sedentary_suggestion())
        return getattr(self, '_last_anti_sedentary_suggestion')
    
    @property
    def last_anti_sedentary_suggestion_datetime(self):
        if self.last_anti_sedentary_suggestion:
            return self.last_anti_sedentary_suggestion.time
        else:
            return None

    @property
    def morning_messages_enabled(self):
        return self._is_configuration_enabled(
            model = MorningMessageConfiguration,
            keyname = '_morning_message_enabled'
        )

    @property
    def date_last_morning_message_survey_completed(self):
        if not self.user:
            return None
        survey = MorningMessageSurvey.objects.filter(
            user = self.user,
            answered = True
        ).order_by('created').last()
        if survey:
            morning_message = MorningMessage.objects.get(
                survey = survey
            )
            return morning_message.date
        return None

    def watch_app_installed_date(self):
        return None
        install = WatchInstall.objects.filter(
            user = self.user
        ).order_by('created').last()
        if install:
            return install.created
        else:
            return None

    def last_watch_app_data(self):
        return None
        last_step_count = WatchAppStepCount.objects.filter(
            user = self.user
        ).order_by('start').last()
        if last_step_count:
            return last_step_count.created
        else:
            return None

    @property
    def last_text_sent(self):
        return None
        try:
            if self.user:
                contact = SMSContact.objects.get(user=self.user)
                sms_message = SMSMessage.objects.filter(recipient=contact.number).order_by('created').last()
                if sms_message:
                    return sms_message.created
            return None
        except SMSContact.DoesNotExist:
            return None

    @property
    def burst_period_configured(self):
        if self.burst_period_configuration is not None:
            return True
        else:
            return False
    
    @property
    def burst_period_enabled(self):
        if self.burst_period_configuration is not None:
            return self.burst_period_configuration.enabled
        else:
            return False

    @property
    def burst_period_configuration(self):
        if not hasattr(self, '_burst_period_configuration'):
            self._burst_period_configuration = self.get_burst_period_configuration()
        return self._burst_period_configuration

    @property
    def burst_periods(self):
        if self.burst_period_configuration:
            return self.burst_period_configuration.burst_periods
        else:
            return []

    @property
    def next_burst_period(self):
        if self.next_burst_periods:
            return self.next_burst_periods[0]
        else:
            return None

    @property
    def next_burst_periods(self):
        if self.burst_period_configuration:
            return self.burst_period_configuration.next_burst_periods
        else:
            return []

    @property
    def previous_burst_periods(self):
        if self.burst_period_configuration:
            return self.burst_period_configuration.previous_burst_periods
        else:
            return []
    
    @property
    def current_burst_period(self):
        if self.burst_period_configuration:
            return self.burst_period_configuration.current_burst_period
        else:
            return None
    
    def get_burst_period_configuration(self):
        if not self.user:
            return None
        try:
            return BurstPeriodConfiguration.objects.get(
                user = self.user
            )
        except BurstPeriodConfiguration.DoesNotExist:
            return None


    @property
    def activity_survey_configuration(self):
        if not hasattr(self, '_activity_survey_configuration'):
            self._activity_survey_configuration = self.get_activity_survey_configuration()
        return self._activity_survey_configuration

    def get_activity_survey_configuration(self):
        if self.user:
            try:
                return ActivitySurveyConfiguration.objects.get(
                    user = self.user
                )
            except ActivitySurveyConfiguration.DoesNotExist:
                return None
        return None

    @property
    def walking_suggestion_survey_configuration(self):
        if not hasattr(self, '_walking_suggestion_survey_configuraiton'):
            self._walking_suggestion_survey_configuraiton = self.get_walking_suggestion_configuration()
        return self._walking_suggestion_survey_configuraiton

    def get_walking_suggestion_configuration(self):
        if not self.user:
            return None
        try:
            return WalkingSuggestionSurveyConfiguration.objects.get(user = self.user)
        except WalkingSuggestionSurveyConfiguration.DoesNotExist:
            return None

    @property
    def walking_suggestion_survey_configuration(self):
        if not hasattr(self, '_walking_suggestion_survey_configuration'):
            self._walking_suggestion_survey_configuraiton = self.get_walking_suggestion_configuration()
        return self._walking_suggestion_survey_configuraiton

    def get_walking_suggestion_configuration(self):
        if not self.user:
            return None
        try:
            return WalkingSuggestionSurveyConfiguration.objects.get(user=self.user)
        except WalkingSuggestionSurveyConfiguration.DoesNotExist:
            return None

class FitbitServiceDashboard(FitbitService):

    def __init__(self, user=None):
        # Need to bring in _FitbitService__account
        # Original method uses __account which resolves to the above
        try:
            super(FitbitServiceDashboard, self).__init__(user=user)
            self._FitbitService__account = self.account
        except FitbitService.NoAccount:
            self.account = None
            self._FitbitService__account = None
            self.__user = user

    def get_account(user):
        try:
            return super(FitbitServiceDashboard, self).get_account()
        except FitbitServiceDashboard.NoAccount:
            return None

    def last_updated_on(self):
        try:
            return super(FitbitServiceDashboard, self).last_updated_on()
        except FitbitServiceDashboard.AccountNeverUpdated:
            return None
