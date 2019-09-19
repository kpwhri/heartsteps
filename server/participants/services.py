from datetime import datetime, timedelta, date

from rest_framework.authtoken.models import Token

from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from adherence_messages.services import AdherenceService
from anti_sedentary.models import Configuration as AntiSedentaryConfiguration
from anti_sedentary.services import AntiSedentaryService
from heartsteps_data_download.tasks import export_user_data
from fitbit_activities.services import FitbitDayService
from morning_messages.models import Configuration as MorningMessagesConfiguration
from sms_messages.models import Contact as SMSContact
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.services import WalkingSuggestionService
from walking_suggestions.tasks import nightly_update as walking_suggestions_nightly_update
from weather.services import WeatherService

from .models import Participant, User

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
        self.enable()

    def is_enabled(self):
        pass

    def enable(self):
        AntiSedentaryConfiguration.objects.update_or_create(
            user = self.participant.user
        )
        MorningMessagesConfiguration.objects.update_or_create(
            user=self.participant.user
        )
        WalkingSuggestionConfiguration.objects.update_or_create(
            user=self.participant.user
        )
        AdherenceMessageConfiguration.objects.update_or_create(
            user = self.participant.user,
            defaults = {
                'enabled': True
            }
        )
        try:
            sms_contact = SMSContact.objects.get(user = self.user)
            sms_contact.enabled = True
            sms_contact.save()
        except SMSContact.DoesNotExist:
            pass
    
    def disable(self):
        AntiSedentaryConfiguration.objects.filter(user = self.participant.user).update(enabled = False)
        MorningMessagesConfiguration.objects.filter(user = self.participant.user).update(enabled = False)
        WalkingSuggestionConfiguration.objects.filter(user = self.participant.user).update(enabled = False)
        AdherenceMessageConfiguration.objects.filter(user = self.participant.user).update(enabled = False)
    
    def update(self, date):        
        self.update_fitbit(date)
        self.update_adherence(date)
        self.update_weather_forecasts(date)

        self.update_anti_sedentary(date)
        self.update_walking_suggestions(date)

        self.queue_data_export()

    def update_fitbit(self, date):
        try:
            fitbit_day = FitbitDayService(
                user = self.participant.user,
                date = date
            )
            fitbit_day.update()
        except FitbitDayService.NoAccount:
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
            anti_sedentary_service.update(date)
        except (AntiSedentaryService.NoConfiguration, AntiSedentaryService.Unavailable, AntiSedentaryService.RequestError):
            pass

    def update_walking_suggestions(self, date):
        try:
            walking_suggestion_service = WalkingSuggestionService(
                user = self.user
            )
            walking_suggestion_service.nightly_update(date)
        except (WalkingSuggestionService.Unavailable, WalkingSuggestionService.RequestError) as e:
            pass

    def update_weather_forecasts(self, date):
        try:
            weather_service = WeatherService(user = self.user)
            weather_service.update_daily_forecast(date)
            weather_service.update_forecasts()
        except (WeatherService.UnknownLocation, WeatherService.ForecastUnavailable):
            pass
    
    def queue_data_export(self):
        export_user_data.apply_async(kwargs={
            'username': self.user.username
        })
