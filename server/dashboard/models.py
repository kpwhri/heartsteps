from datetime import date
from datetime import timedelta

from django.db import models

from adherence_messages.models import AdherenceMetric
from adherence_messages.models import AdherenceMessage
from adherence_messages.services import (
    AdherenceAppInstallMessageService,
    AdherenceFitbitUpdatedService
)
from anti_sedentary.models import AntiSedentaryDecision
from days.services import DayService
from fitbit_api.models import (FitbitAccount, FitbitAccountUser)
from fitbit_api.services import FitbitService
from participants.models import Participant
from randomization.models import UnavailableReason
from sms_messages.models import (Contact, Message)
from walking_suggestions.models import WalkingSuggestionDecision
from watch_app.models import StepCount as WatchAppStepCount

from anti_sedentary.models import Configuration as AntiSedentaryConfiguration
from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from morning_messages.models import Configuration as MorningMessageConfiguration
from morning_messages.models import MorningMessage
from morning_messages.models import MorningMessageSurvey
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration

from push_messages.models import Message as PushMessage

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

class NotificationsQuerySet(models.QuerySet):

    def get_notifications(self, start, end):
        participants = self.exclude(user=None).all()
        users = [participant.user for participant in participants]

        query = PushMessage.objects.filter(
            recipient__in = users,
            message_type = PushMessage.NOTIFICATION,
            created__gte = start,
            created__lte = end
        )
        return query.all()


class DashboardParticipant(Participant):

    notifications = NotificationsQuerySet.as_manager()
    summaries = InterventionSummaryManager()
    watch_app_step_counts = WatchAppSummaryManager()

    class Meta:
        proxy = True

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
