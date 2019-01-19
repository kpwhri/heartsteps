from datetime import datetime

from django.utils import timezone

from locations.services import LocationService
from randomization.services import DecisionMessageService, DecisionContextService

from anti_sedentary.models import AntiSedentaryDecision, AntiSedentaryMessageTemplate

class AntiSedentaryDecisionService(DecisionMessageService, DecisionContextService):

    MESSAGE_TEMPLATE_MODEL = AntiSedentaryMessageTemplate

    def generate_context(self):
        context = super().generate_context()
        time_of_day_context = self.get_time_of_day_context()
        if time_of_day_context:
            context.append(time_of_day_context)
        return context

    def update_availability(self):
        location_service = LocationService(self.decision.user)
        local_timezone = location_service.get_timezone_on(self.decision.time)
        local_time = self.decision.time.astimezone(local_timezone)

        end_of_day = local_time.replace(hour=20, minute=0)
        start_of_day = local_time.replace(hour=8, minute=0)
        if end_of_day < local_time or start_of_day > local_time:
            self.decision.available = False
            self.decision.save()
        else:
            self.decision.available = True
            self.decision.save()
            super().update_availability()

    def get_time_of_day_context(self):
        location_service = LocationService(self.decision.user)
        local_timezone = location_service.get_timezone_on(self.decision.time)
        local_time = self.decision.time.astimezone(local_timezone)

        start_of_day = local_time.replace(hour=8, minute=0)
        morning_end = local_time.replace(hour=10, minute=30)
        lunch_end = local_time.replace(hour=13, minute=30)
        afternoon_end = local_time.replace(hour=16, minute=30)
        evening_end = local_time.replace(hour=18, minute=30)
        end_of_day = local_time.replace(hour=20, minute=0)

        if start_of_day < self.decision.time <= morning_end:
            return 'morning'
        if morning_end < self.decision.time <= lunch_end:
            return 'lunch'
        if lunch_end < self.decision.time <= afternoon_end:
            return 'midafternoon'
        if afternoon_end < self.decision.time <= evening_end:
            return 'evening'
        if evening_end < self.decision.time <= end_of_day:
            return 'postdinner'

    def create_decision(user, test=False):
        decision = AntiSedentaryDecision.objects.create(
            user = user,
            test = test,
            time = timezone.now()
        )
        return AntiSedentaryDecisionService(decision)