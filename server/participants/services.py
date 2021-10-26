from datetime import datetime, timedelta, date

from django.utils import timezone
from rest_framework.authtoken.models import Token

from activity_surveys.models import Configuration as ActivitySurveyConfiguration
from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from adherence_messages.services import AdherenceService
from anti_sedentary.models import Configuration as AntiSedentaryConfiguration
from anti_sedentary.services import AntiSedentaryService
from burst_periods.models import Configuration as BurstPeriodConfiguration
from days.services import DayService
from fitbit_activities.services import FitbitActivityService
from fitbit_activities.services import FitbitDayService
from fitbit_activities.models import FitbitDay
from fitbit_activities.tasks import update_incomplete_days
from morning_messages.models import Configuration as MorningMessagesConfiguration
from push_messages.models import Message as PushMessage
from sms_messages.models import Contact as SMSContact
from walking_suggestion_surveys.models import Configuration as WalkingSuggestionSurveyConfiguration
from walking_suggestion_times.models import SuggestionTime
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from generic_messages.models import GenericMessagesConfiguration
from walking_suggestions.services import WalkingSuggestionService
from walking_suggestion_times.tasks import create_default_suggestion_times
from walking_suggestions.tasks import nightly_update as walking_suggestions_nightly_update
from weather.services import WeatherService

from nlm.services import StudyTypeService
from feature_flags.models import FeatureFlags

from .models import Participant, User
from .models import NightlyUpdateRecord

from user_event_logs.models import EventLog

class ParticipantService:

    class NoParticipant(Participant.DoesNotExist):
        pass

    def __init__(self, participant=None, user=None, username=None):
        try:
            if username:
                participant = Participant.objects.get(user__username=username)
            if user:
                participant = Participant.objects.get(user=user)
        except Participant.DoesNotExist:
            pass
        if not participant:
            raise ParticipantService.NoParticipant()

        self.participant = participant
        self.user = participant.user

    def get_study(self):
        if not hasattr(self, '_study'):
            if self.participant.cohort and self.participant.cohort.study:
                self._study = self.participant.cohort.study
            else:
                self._study = None
        return self._study

    def get_study_contact_name(self):
        study = self.get_study()
        if study:
            return study.contact_name
        else:
            return None

    def get_study_contact_number(self):
        study = self.get_study()
        if study:
            return study.contact_number
        else:
            return None

    def get_baseline_period(self):
        study = self.get_study()
        if study:
            return study.baseline_period
        else:
            return 0

    def get_participantTags(self):
        tag_list = []
        # TODO: Implement Participant Tags

        # For NLM
        study_type_service = StudyTypeService("NLM", user=self.user)
        if study_type_service.is_cohort_assigned(self.participant.cohort):
            tag_list.append("NLM")

        # TODO: Add more tags if necessary

        return tag_list

    def get_participant(token, birth_year):
        try:
            participant = Participant.objects.get(
                enrollment_token__iexact=token,
                birth_year=birth_year
            )
            return ParticipantService(
                participant=participant
            )
        except Participant.DoesNotExist:
            if len(token) == 8 and "-" not in token:
                new_token = token[:4] + "-" + token[4:]
                return ParticipantService.get_participant(new_token, birth_year)
            raise ParticipantService.NoParticipant('No participant for token')

    def has_authorization_token(self):
        if not self.user:
            False
        try:
            Token.objects.get(user=self.participant.user)
            return True
        except Token.DoesNotExist:
            return False

    def get_authorization_token(self):
        token, _ = Token.objects.get_or_create(user=self.participant.user)
        return token

    def destroy_authorization_token(self):
        Token.objects.filter(user=self.participant.user).delete()

    def get_heartsteps_id(self):
        return self.participant.heartsteps_id

    def initialize(self):
        self.participant.enroll()
        self.participant.set_daily_task()
        create_default_suggestion_times(participant=self.participant)
        self.enable()
        
        if not self.user is None:
            if self.participant is not None:
                if self.participant.cohort is not None:
                    if self.participant.cohort.study is not None:
                        if self.participant.cohort.study.studywide_feature_flags is not None:
                            study_feature_flags = self.participant.cohort.study.studywide_feature_flags
                            FeatureFlags.create_or_update(self.user, study_feature_flags)
                        else:
                            EventLog.error(self.user, "Studywide feature flag doesn't exist: {}".format(self.participant.cohort.study))
                    else:
                        EventLog.error(self.user, "Study doesn't exist: {}".format(self.participant.cohort))
                else:
                    EventLog.error(self.user, "Cohort doesn't exist: {}".format(self.participant))
            else:
                EventLog.error(self.user, "Participant doesn't exist: {}".format(self))
        else:
            EventLog.info(None, "self.user is still None: {}".format(self.participant))

    def is_enabled(self):
        return self.participant.active

    def is_baseline_complete(self):
        EventLog.info(self.user, "is_baseline_complete() initialized.")
        try:
            service = FitbitActivityService(user=self.user)
            EventLog.info(self.user, "FitbitActivityService is initialized.")
        except FitbitActivityService.NoAccount:
            EventLog.info(self.user, "FitbitActivityService is not initialized. No FitbitAccount.")
            return False
        if self.user.is_staff:
            EventLog.info(self.user, "is_staff is true. returning true...")
            return True
        start_date = self.participant.get_study_start_date()
        EventLog.info(self.user, "participant.get_study_start_date(): {}".format(start_date))
        if start_date:
            days_worn = service.get_days_worn(start_date)
            EventLog.info(self.user, "start_date is not None. service.get_days_worn(): {}".format(days_worn))
        else:
            days_worn = service.get_days_worn()
            EventLog.info(self.user, "start_date is None. service.get_days_worn(): {}".format(days_worn))
        baseline_period = self.get_baseline_period()
        EventLog.info(self.user, "baseline_period: {}".format(baseline_period))
        if days_worn >= baseline_period:
            EventLog.info(self.user, "days_worn >= basline_period. returning true")
            return True
        else:
            EventLog.info(self.user, "days_worn < basline_period. returning false")
            return False

    def enable(self):
        self.participant.active = True
        self.participant.save()

        adherence_message_configuration, _ = AdherenceMessageConfiguration.objects.update_or_create(
            user=self.participant.user
        )
        adherence_message_configuration.enabled = True
        adherence_message_configuration.save()

        try:
            burst_period_configuration = BurstPeriodConfiguration.objects.get(
                user=self.participant.user
            )
        except BurstPeriodConfiguration.DoesNotExist:
            burst_period_configuration = BurstPeriodConfiguration.objects.create(
                user=self.participant.user
            )

        if self.is_baseline_complete():
            anti_sedentary_configuration, _ = AntiSedentaryConfiguration.objects.update_or_create(
                user=self.participant.user
            )
            anti_sedentary_configuration.enabled = True
            anti_sedentary_configuration.save()

            morning_message_configuration, _ = MorningMessagesConfiguration.objects.update_or_create(
                user=self.participant.user
            )
            morning_message_configuration.enabled = True
            morning_message_configuration.save()

            try:
                walking_suggestion_configuration, _ = WalkingSuggestionConfiguration.objects.update_or_create(
                    user=self.participant.user
                )
                walking_suggestion_configuration.enabled = True
                walking_suggestion_configuration.save()
            except WalkingSuggestionConfiguration.MultipleObjectsReturned:
                pass

            try:
                activity_survey_configuration = ActivitySurveyConfiguration.objects.get(
                    user=self.participant.user
                )
                activity_survey_configuration.enabled = True
                activity_survey_configuration.save()
            except ActivitySurveyConfiguration.DoesNotExist:
                ActivitySurveyConfiguration.objects.create(
                    user=self.participant.user,
                    enabled=True
                )

            try:
                walking_suggestion_survey_configuration = WalkingSuggestionSurveyConfiguration.objects.get(
                    user=self.participant.user
                )
                walking_suggestion_survey_configuration.enabled = True
                walking_suggestion_survey_configuration.save()
            except WalkingSuggestionSurveyConfiguration.DoesNotExist:
                WalkingSuggestionSurveyConfiguration.objects.create(
                    user=self.participant.user,
                    enabled=True
                )

    def disable(self):
        self.participant.active = False
        self.participant.save()
        try:
            activity_survey_configuration = ActivitySurveyConfiguration.objects.get(
                user=self.participant.user
            )
            activity_survey_configuration.enabled = False
            activity_survey_configuration.save()
        except ActivitySurveyConfiguration.DoesNotExist:
            pass
        try:
            walking_suggestion_survey_configuration = WalkingSuggestionSurveyConfiguration.objects.get(
                user=self.participant.user
            )
            walking_suggestion_survey_configuration.enabled = False
            walking_suggestion_survey_configuration.save()
        except WalkingSuggestionSurveyConfiguration.DoesNotExist:
            pass
        AntiSedentaryConfiguration.objects.filter(
            user=self.participant.user).update(enabled=False)
        MorningMessagesConfiguration.objects.filter(
            user=self.participant.user).update(enabled=False)
        WalkingSuggestionConfiguration.objects.filter(
            user=self.participant.user).update(enabled=False)
        AdherenceMessageConfiguration.objects.filter(
            user=self.participant.user).update(enabled=False)

    def update(self, date=None):
        EventLog.info(self.participant.user, "ParticipantService.update() initiated.")
        
        if date is None:
            EventLog.info(self.participant.user, "  date is None. Replacing with yesterday.")
            day_service = DayService(user=self.participant.user)
            date = day_service.get_current_date() - timedelta(days=1)
            
        update_record = NightlyUpdateRecord(
            user=self.participant.user,
            date=date,
            start=timezone.now()
        )
        try:
            if self.is_baseline_complete():
                EventLog.info(self.participant.user, "  self.is_baseline_complete is true.")
                try:
                    AntiSedentaryConfiguration.objects.get(
                        user=self.participant.user)
                    EventLog.info(self.participant.user, "  AntiSedentaryConfiguration object is found.")
                except AntiSedentaryConfiguration.DoesNotExist:
                    AntiSedentaryConfiguration.objects.create(
                        user=self.participant.user,
                        enabled=True
                    )
                    EventLog.info(self.participant.user, "  AntiSedentaryConfiguration object is created.")
                try:
                    MorningMessagesConfiguration.objects.get(
                        user=self.participant.user)
                    EventLog.info(self.participant.user, "  MorningMessagesConfiguration object is found.")
                except MorningMessagesConfiguration.DoesNotExist:
                    MorningMessagesConfiguration.objects.create(
                        user=self.participant.user,
                        enabled=True
                    )
                    EventLog.info(self.participant.user, "  MorningMessagesConfiguration object is created.")
                try:
                    WalkingSuggestionConfiguration.objects.get(
                        user=self.participant.user)
                    EventLog.info(self.participant.user, "  WalkingSuggestionConfiguration object is found.")
                except WalkingSuggestionConfiguration.DoesNotExist:
                    WalkingSuggestionConfiguration.objects.create(
                        user=self.participant.user,
                        enabled=True
                    )
                    EventLog.info(self.participant.user, "  WalkingSuggestionConfiguration object is created.")
                try:
                    ActivitySurveyConfiguration.objects.get(
                        user=self.participant.user
                    )
                    EventLog.info(self.participant.user, "  ActivitySurveyConfiguration object is found.")
                except ActivitySurveyConfiguration.DoesNotExist:
                    ActivitySurveyConfiguration.objects.create(
                        user=self.participant.user,
                        enabled=True
                    )
                    EventLog.info(self.participant.user, "  ActivitySurveyConfiguration object is created.")
                try:
                    wss_config = WalkingSuggestionSurveyConfiguration.objects.get(
                        user=self.participant.user
                    )
                    EventLog.info(self.participant.user, "  WalkingSuggestionSurveyConfiguration object is found.")
                except WalkingSuggestionSurveyConfiguration.DoesNotExist:
                    wss_config = WalkingSuggestionSurveyConfiguration.objects.create(
                        user=self.participant.user,
                        enabled=True
                    )
                    EventLog.info(self.participant.user, "  WalkingSuggestionSurveyConfiguration object is created.")
                try:
                    GenericMessagesConfiguration.objects.get(
                        user=self.participant.user
                    )
                    EventLog.info(self.participant.user, "  GenericMessagesConfiguration object is found.")
                except GenericMessagesConfiguration.DoesNotExist:
                    GenericMessagesConfiguration.objects.create(
                        user=self.participant.user,
                        enabled=True
                    )
                    EventLog.info(self.participant.user, "  GenericMessagesConfiguration object is created.")
            else:
                EventLog.info(self.participant.user, "  self.is_baseline_complete is false.")

            EventLog.info(self.participant.user, "  ParticipantService.update_fitbit() is running")
            self.update_fitbit(date)
            EventLog.info(self.participant.user, "  ParticipantService.update_message_receipts() is running")
            self.update_message_receipts(date)
            EventLog.info(self.participant.user, "  ParticipantService.update_adherence() is running")
            self.update_adherence(date)
            EventLog.info(self.participant.user, "  ParticipantService.update_weather_forecasts() is running")
            self.update_weather_forecasts(date)
            EventLog.info(self.participant.user, "  ParticipantService.update_anti_sedentary() is running")
            self.update_anti_sedentary(date)
            EventLog.info(self.participant.user, "  ParticipantService.update_walking_suggestions() is running")
            self.update_walking_suggestions(date)
        except Exception as e:
            update_record.error = e
            EventLog.error(self.participant.user, "  ParticipantService.update() error: {}".format(e))
        update_record.end = timezone.now()
        update_record.save()
        EventLog.info(self.participant.user, "ParticipantService.update() finished.")

    def update_fitbit(self, date):
        EventLog.info(self.participant.user, "ParticipantService.update_fitbit() is called")
        try:
            service = FitbitActivityService(
                user=self.participant.user
            )
            EventLog.info(self.participant.user, "FitbitActivityService is created")

            # temporary to update minutes worn
            days_with_no_minutes_worn = FitbitDay.objects.filter(
                account=service.account,
                minutes_worn=None
            ).prefetch_related('account').all()
            EventLog.info(self.participant.user, "FitbitDays with no minutes are fetched: {}".format(days_with_no_minutes_worn))
            for _day in days_with_no_minutes_worn:
                EventLog.info(self.participant.user, "This FitbitDay has no minutes. Refreshing: {}".format(_day))
                _day.save()
                EventLog.info(self.participant.user, "---> refreshed: {}".format(_day))

            incomplete_dates = [_d.date for _d in FitbitDay.objects.filter(
                account=service.account, completely_updated=False).all()]
            EventLog.info(self.participant.user, "FitbitDays with incomplete minutes are fetched: {}".format(incomplete_dates))
            if date not in incomplete_dates:
                EventLog.info(self.participant.user, "This FitbitDay is incomplete. Refreshing: {}".format(date))
                incomplete_dates.append(date)
                EventLog.info(self.participant.user, "---> refreshed: {}".format(date))
            for _date in sorted(incomplete_dates):
                service.update(_date)
            EventLog.info(self.participant.user, "All incomplete days have been filled.")
        except FitbitActivityService.TooManyRequests:
            EventLog.info(self.participant.user, "Fitbit server rejected due to too many requests. Retrying in 90 minutes.")
            update_incomplete_days.apply_async(
                eta=timezone.now() + timedelta(minutes=90),
                kwargs={
                    'fitbit_user': service.account.fitbit_user
                }
            )
        except FitbitActivityService.Unauthorized:
            EventLog.info(self.participant.user, "Fitbit server rejected due to unauthorized requests. Not going to retry.")
        except FitbitActivityService.NoAccount:
            EventLog.info(self.participant.user, "Fitbit server rejected due to no account. Not going to retry.")

    def update_adherence(self, date):
        EventLog.info(self.user, "update_adherence() is called")
        try:
            service = AdherenceService(user=self.user)
            EventLog.info(self.user, "AdherenceService is initialized: {}".format(service))
            service.update_adherence(date)
            EventLog.info(self.user, "service.update_adherence({}) is called".format(date))
        except AdherenceService.NoConfiguration:
            EventLog.error(self.user, "AdherenceService.NoConfiguration")

    def update_anti_sedentary(self, date):
        EventLog.info(self.user, "update_anti_sedentary() is called")
        try:
            anti_sedentary_service = AntiSedentaryService(
                user=self.user
            )
            EventLog.info(self.user, "AntiSedentaryService is initialized: {}".format(anti_sedentary_service))
            if self.is_enabled() and self.is_baseline_complete():
                anti_sedentary_service.enable()
                EventLog.info(self.user, "AntiSedentaryService is turned on: {}".format(anti_sedentary_service))
            anti_sedentary_service.update(date)
            EventLog.info(self.user, "AntiSedentaryService is updated: {}".format(anti_sedentary_service))
        except (AntiSedentaryService.NoConfiguration, AntiSedentaryService.Unavailable, AntiSedentaryService.RequestError) as e:
            EventLog.error(self.user, "AntiSedentaryService error: {}".format(e))

    def update_walking_suggestions(self, date):
        EventLog.info(self.user, "update_walking_suggestions() is called")
        try:
            walking_suggestion_service = WalkingSuggestionService(
                user=self.user
            )
            EventLog.info(self.user, "WalkingSuggestionService")
            if self.is_enabled() and self.is_baseline_complete():
                walking_suggestion_service.enable()
                EventLog.info(self.user, "Walking suggestion is turned on")
            walking_suggestion_service.nightly_update(date)
            EventLog.info(self.user, "walking_suggestion_service.nightly_update({})".format(date))
        except (WalkingSuggestionService.Unavailable, WalkingSuggestionService.UnableToInitialize, WalkingSuggestionService.RequestError) as e:
            EventLog.error(self.user, "walking_suggestion_service error: {}".format(e))

    def update_weather_forecasts(self, date):
        EventLog.info(self.user, "Update weather forecast is called")
        try:
            weather_service = WeatherService(user=self.user)
            EventLog.info(self.user, "Weather service is created: {}".format(weather_service))
            weather_service.update_daily_forecast(date)
            EventLog.info(self.user, "Daily Forecast is updated: {}".format(weather_service))
            weather_service.update_forecasts()
            EventLog.info(self.user, "Forecasts are updated: {}".format(weather_service))
        except (WeatherService.UnknownLocation, WeatherService.ForecastUnavailable) as e:
            EventLog.error(self.user, "Exception during Forecast update: {}".format(e))

    def update_message_receipts(self, date):
        EventLog.info(self.user, "Update message receipt initialized.")
        if not self.user:
            EventLog.info(self.user, "self.user is none.")
            return
        day_service = DayService(user=self.user)
        EventLog.info(self.user, "day service is created.")
        messages = PushMessage.objects.filter(
            recipient=self.user,
            created__gte=day_service.get_start_of_day(date),
            created__lte=day_service.get_end_of_day(date)
        ).all()
        EventLog.info(self.user, "All messages sent today are fetched.")
        for message in messages:
            EventLog.info(self.user, "Updating message receipt: {}".format(message))
            message.update_message_receipts()
