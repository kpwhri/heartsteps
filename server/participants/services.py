from datetime import datetime, timedelta, date

from rest_framework.authtoken.models import Token

from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from adherence_messages.services import AdherenceService
from anti_sedentary.models import Configuration as AntiSedentaryConfiguration
from anti_sedentary.services import AntiSedentaryService
from days.services import DayService
from heartsteps_data_download.tasks import export_user_data
from fitbit_activities.services import FitbitDayService
from morning_messages.models import Configuration as MorningMessagesConfiguration
from sms_messages.models import Contact as SMSContact
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.services import WalkingSuggestionService
from walking_suggestions.tasks import nightly_update as walking_suggestions_nightly_update

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
    
    def get_authorization_token(self):
        token, _ = Token.objects.get_or_create(user=self.participant.user)
        return token
    
    def get_heartsteps_id(self):
        return self.participant.heartsteps_id

    def get_current_datetime(self):
        service = DayService(user=self.participant.user)
        timezone = service.get_current_timezone()
        return datetime.now(timezone)

    def initialize(self):
        self.participant.enroll()
        self.participant.set_daily_task()
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
    
    def deactivate(self):
        pass
    
    def update(self, day=None):
        if not day:
            day = self.get_current_datetime()
        self.update_fitbit(day)
        self.update_adherence(day)

        self.update_anti_sedentary(day)
        self.update_walking_suggestions(day)

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
        except (AntiSedentaryService.NoConfiguration, AntiSedentaryService.Unavailable):
            pass

    def update_walking_suggestions(self, date):
        walking_suggestions_nightly_update(
            username = self.user.username,
            day_string = date.strftime('%Y-%m-%d')
        )
    
    def queue_data_export(self):
        export_user_data.apply_async(kwargs={
            'username': self.user.username
        })
