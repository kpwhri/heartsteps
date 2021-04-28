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
from walking_suggestions.services import WalkingSuggestionService
from walking_suggestions.tasks import nightly_update as walking_suggestions_nightly_update
from weather.services import WeatherService

from .models import Participant, User
from .models import NightlyUpdateRecord

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

    def get_participant(token, birth_year):
        try:
            participant = Participant.objects.get(
                enrollment_token__iexact=token,
                birth_year = birth_year
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
        Token.objects.filter(user = self.participant.user).delete()
    
    def get_heartsteps_id(self):
        return self.participant.heartsteps_id

    def initialize(self):
        self.participant.enroll()
        self.participant.set_daily_task()
        self.create_default_suggestion_times()
        self.enable()

    def is_enabled(self):
        return self.participant.active

    def is_baseline_complete(self):
        try:
            service = FitbitActivityService(user=self.user)
        except FitbitActivityService.NoAccount:
            return False
        if self.user.is_staff:
            return True
        start_date = self.participant.get_study_start_date()
        if start_date:
            days_worn = service.get_days_worn(start_date)
        else:
            days_worn = service.get_days_worn()
        if days_worn >= self.get_baseline_period():
            return True
        return False

    def enable(self):
        self.participant.active = True
        self.participant.save()

        adherence_message_configuration, _ = AdherenceMessageConfiguration.objects.update_or_create(
            user = self.participant.user
        )
        adherence_message_configuration.enabled = True
        adherence_message_configuration.save()

        try:
            burst_period_configuration = BurstPeriodConfiguration.objects.get(
                user = self.participant.user
            )
        except BurstPeriodConfiguration.DoesNotExist:
            burst_period_configuration = BurstPeriodConfiguration.objects.create(
                user = self.participant.user
            )

        if self.is_baseline_complete():
            anti_sedentary_configuration, _ = AntiSedentaryConfiguration.objects.update_or_create(
                user = self.participant.user
            )
            anti_sedentary_configuration.enabled = True
            anti_sedentary_configuration.save()

            morning_message_configuration, _ = MorningMessagesConfiguration.objects.update_or_create(
                user=self.participant.user
            )
            morning_message_configuration.enabled = True
            morning_message_configuration.save()

            walking_suggestion_configuration, _ = WalkingSuggestionConfiguration.objects.update_or_create(
                user=self.participant.user
            )
            walking_suggestion_configuration.enabled = True
            walking_suggestion_configuration.save()

            try:
                activity_survey_configuration = ActivitySurveyConfiguration.objects.get(
                    user = self.participant.user
                )
                activity_survey_configuration.enabled = True
                activity_survey_configuration.save()
            except ActivitySurveyConfiguration.DoesNotExist:
                ActivitySurveyConfiguration.objects.create(
                    user = self.participant.user,
                    enabled = True
                )

            try:
                walking_suggestion_survey_configuration = WalkingSuggestionSurveyConfiguration.objects.get(
                    user = self.participant.user
                )
                walking_suggestion_survey_configuration.enabled = True
                walking_suggestion_survey_configuration.save()
            except WalkingSuggestionSurveyConfiguration.DoesNotExist:
                WalkingSuggestionSurveyConfiguration.objects.create(
                    user = self.participant.user,
                    enabled = True
                )

    
    def disable(self):
        self.participant.active = False
        self.participant.save()
        try:
            activity_survey_configuration = ActivitySurveyConfiguration.objects.get(
                user = self.participant.user
            )
            activity_survey_configuration.enabled = False
            activity_survey_configuration.save()
        except ActivitySurveyConfiguration.DoesNotExist:
            pass
        try:
            walking_suggestion_survey_configuration = WalkingSuggestionSurveyConfiguration.objects.get(
                user = self.participant.user
            )
            walking_suggestion_survey_configuration.enabled = False
            walking_suggestion_survey_configuration.save()
        except WalkingSuggestionSurveyConfiguration.DoesNotExist:
            pass
        AntiSedentaryConfiguration.objects.filter(user = self.participant.user).update(enabled = False)
        MorningMessagesConfiguration.objects.filter(user = self.participant.user).update(enabled = False)
        WalkingSuggestionConfiguration.objects.filter(user = self.participant.user).update(enabled = False)
        AdherenceMessageConfiguration.objects.filter(user = self.participant.user).update(enabled = False)

    def create_default_suggestion_times(self):
        existing_suggestion_times = SuggestionTime.objects.filter(
            user=self.participant.user
        ).count()
        if not existing_suggestion_times:
            default_times = [
                (SuggestionTime.MORNING, 8, 0),
                (SuggestionTime.LUNCH, 12, 0),
                (SuggestionTime.MIDAFTERNOON, 14, 0),
                (SuggestionTime.EVENING, 5, 0),
                (SuggestionTime.POSTDINNER, 20, 0)
            ]
            for category, hour, minute in default_times:
                SuggestionTime.objects.create(
                    user = self.participant.user,
                    category = category,
                    hour = hour,
                    minute = minute
                )
    
    def update(self, date):
        update_record = NightlyUpdateRecord(
            user = self.participant.user,
            date = date,
            start = timezone.now()
        )
        try:
            if self.is_baseline_complete():
                try:
                    AntiSedentaryConfiguration.objects.get(user = self.participant.user)
                except AntiSedentaryConfiguration.DoesNotExist:
                    AntiSedentaryConfiguration.objects.create(
                        user = self.participant.user,
                        enabled = True
                    )
                try:
                    MorningMessagesConfiguration.objects.get(user = self.participant.user)
                except MorningMessagesConfiguration.DoesNotExist:
                    MorningMessagesConfiguration.objects.create(
                        user = self.participant.user,
                        enabled = True
                    )
                try:
                    WalkingSuggestionConfiguration.objects.get(user = self.participant.user)
                except WalkingSuggestionConfiguration.DoesNotExist:
                    WalkingSuggestionConfiguration.objects.create(
                        user = self.participant.user,
                        enabled = True
                    )
                try:
                    ActivitySurveyConfiguration.objects.get(
                        user = self.participant.user
                    )
                except ActivitySurveyConfiguration.DoesNotExist:
                    ActivitySurveyConfiguration.objects.create(
                        user = self.participant.user,
                        enabled = True
                    )
                try:
                    wss_config = WalkingSuggestionSurveyConfiguration.objects.get(
                        user = self.participant.user
                    )
                except WalkingSuggestionSurveyConfiguration.DoesNotExist:
                    wss_config = WalkingSuggestionSurveyConfiguration.objects.create(
                        user = self.participant.user,
                        enabled = True
                    )
                wss_config.update_survey_times()
                

            self.update_fitbit(date)
            self.update_message_receipts(date)
            self.update_adherence(date)
            self.update_weather_forecasts(date)

            self.update_anti_sedentary(date)
            self.update_walking_suggestions(date)
        except Exception as e:
            update_record.error = e
        update_record.end = timezone.now()
        update_record.save()

    def update_fitbit(self, date):
        try:
            service = FitbitActivityService(
                user = self.participant.user
            )

            #temporary to update minutes worn
            days_with_no_minutes_worn = FitbitDay.objects.filter(
                account=service.account,
                minutes_worn = None
            ).prefetch_related('account').all()
            for _day in days_with_no_minutes_worn:
                _day.save()

            incomplete_dates = [_d.date for _d in FitbitDay.objects.filter(account=service.account, completely_updated=False).all()]
            if date not in incomplete_dates:
                incomplete_dates.append(date)
            for _date in sorted(incomplete_dates):
                service.update(_date)
        except FitbitActivityService.TooManyRequests:
            update_incomplete_days.apply_async(
                eta = timezone.now() + timedelta(minutes=90),
                kwargs = {
                    'fitbit_user': service.account.fitbit_user
                }
            )
        except FitbitActivityService.Unauthorized:
            pass
        except FitbitActivityService.NoAccount:
            pass

    def update_adherence(self, date):
        try:
            service = AdherenceService(user = self.user)
            service.update_adherence(date)
        except AdherenceService.NoConfiguration:
            pass

    def update_anti_sedentary(self, date):
        try:
            anti_sedentary_service = AntiSedentaryService(
                user = self.user
            )
            if self.is_enabled() and self.is_baseline_complete():
                anti_sedentary_service.enable()
            anti_sedentary_service.update(date)
        except (AntiSedentaryService.NoConfiguration, AntiSedentaryService.Unavailable, AntiSedentaryService.RequestError):
            pass

    def update_walking_suggestions(self, date):
        try:
            walking_suggestion_service = WalkingSuggestionService(
                user = self.user
            )
            if self.is_enabled() and self.is_baseline_complete():
                walking_suggestion_service.enable()
            walking_suggestion_service.nightly_update(date)
        except (WalkingSuggestionService.Unavailable, WalkingSuggestionService.UnableToInitialize, WalkingSuggestionService.RequestError) as e:
            pass

    def update_weather_forecasts(self, date):
        try:
            weather_service = WeatherService(user = self.user)
            weather_service.update_daily_forecast(date)
            weather_service.update_forecasts()
        except (WeatherService.UnknownLocation, WeatherService.ForecastUnavailable):
            pass

    def update_message_receipts(self, date):
        if not self.user:
            return
        day_service = DayService(user=self.user)
        messages = PushMessage.objects.filter(
            recipient = self.user,
            created__gte = day_service.get_start_of_day(date),
            created__lte = day_service.get_end_of_day(date)
        ).all()
        for message in messages:
            message.update_message_receipts()
