from datetime import datetime, timedelta, date

from rest_framework.authtoken.models import Token

from days.services import DayService
from fitbit_activities.services import FitbitDayService
from anti_sedentary.models import Configuration as AntiSedentaryConfiguration
from anti_sedentary.services import AntiSedentaryService
from morning_messages.models import Configuration as MorningMessagesConfiguration
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.services import WalkingSuggestionService

from .models import Participant, User
from .signals import nightly_update

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
    
    def deactivate(self):
        pass
    
    def update(self, day=None):
        if not day:
            day = self.get_current_datetime()

        try:
            fitbit_day = FitbitDayService(
                user = self.participant.user,
                date = day
            )
            fitbit_day.update()
        except FitbitDayService.NoAccount:
            pass

        nightly_update.send(
            sender = User,
            user = self.participant.user,
            day = date(day.year, day.month, day.day)
        )

        try:
            anti_sedentary_service = AntiSedentaryService(
                user = self.participant.user
            )
            anti_sedentary_service.update(day)
        except (AntiSedentaryService.NoConfiguration, AntiSedentaryService.Unavailable):
            pass
