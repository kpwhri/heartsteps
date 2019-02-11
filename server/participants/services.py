from datetime import datetime, timedelta

from fitbit_api.services import FitbitDayService
from locations.services import LocationService
from morning_messages.models import Configuration as MorningMessagesConfiguration
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.services import WalkingSuggestionService

from .models import Participant

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

    def get_current_datetime(self):
        location_service = LocationService(self.participant.user)
        timezone = location_service.get_current_timezone()
        return datetime.now(timezone)

    def enroll(self):
        self.participant.set_daily_task()
        MorningMessagesConfiguration.objects.update_or_create(
            user=self.participant.user
        )
        WalkingSuggestionConfiguration.objects.update_or_create(
            user=self.participant.user
        )
    
    def unenroll(self):
        pass
    
    def update(self, day=None):
        if not day:
            day = self.get_current_datetime()

        ## Create "Onboarding app" to contain this logic
        # If participant doesn't have active push device
        # AND datetime > number of days for baseline
        # Send text message prompt

        # Study adherence nightly update run
        ## Looks at participant data, sends activity alerts
        try:
            fitbit_day = FitbitDayService(
                user = self.participant.user,
                date = day
            )
            fitbit_day.update()
        except FitbitDayService.NoAccount:
            pass

        try:
            walking_suggestion_service = WalkingSuggestionService(
                user = self.participant.user
            )
            walking_suggestion_service.update(day)
        except WalkingSuggestionService.Unavailable:
            pass

        ## Maybe following is just update task from app
        # if walking suggestions configuration has suggestion times
        # AND
        # activity suggestion service is available
        # THEN
        # if service not initialized, initialize service
        # else update service