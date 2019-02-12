from datetime import datetime

from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from anti_seds.models import StepCount
from locations.services import LocationService
from randomization.services import DecisionMessageService, DecisionContextService

from anti_sedentary.models import AntiSedentaryDecision, AntiSedentaryMessageTemplate, Configuration

class AntiSedentaryService:

    class NoConfiguration(ImproperlyConfigured):
        pass
    
    class NoSteps(ValueError):
        pass

    def __init__(self, configuration=None, user=None, username=None):
        try:
            if username:
                configuration = Configuration.objects.get(user__username=username)
            if user:
                configuration = Configuration.objects.get(user=user)
        except Configuration.DoesNotExist:
            raise AntiSedentaryService.NoConfiguration('No configuration found')
        if not configuration:
            raise AntiSedentaryService.NoConfiguration('No configuration')
        self.__configuration = configuration
        self.__user = configuration.user

    def create_decision(self):
        decision = AntiSedentaryDecision.objects.create(
            user = self.__user,
            time = timezone.now()
        )
        return decision

    def time_within_day(self, time):
        location_service = LocationService(self.__user)
        local_timezone = location_service.get_timezone_on(time)
        local_time = time.astimezone(local_timezone)

        end_of_day = local_time.replace(hour=20, minute=0)
        start_of_day = local_time.replace(hour=8, minute=0)

        if time > start_of_day and time < end_of_day:
            return True
        else:
            return False

    def can_randomize_now(self):
        now = timezone.now()
        return self.can_randomize(now)

    def can_randomize(self, time):
        if not self.__configuration.enabled:
            return False
        if self.time_within_day(time):
            return True
        else:
            return False

    def enable(self):
        if not self.__configuration.enabled:
            self.__configuration.enabled = True
            self.__configuration.save()

    def get_step_count_at(self, time):
        step_count = StepCount.objects.filter(
            user = self.__user,
            step_dtm__lte=time
        ).first()
        if not step_count:
            raise AntiSedentaryService.NoSteps('No steps found')
        return step_count.step_number

    def get_step_count_change_at(self, time):
        step_counts = StepCount.objects.filter(
            user = self.__user,
            step_dtm__lte = time
        )[:2]
        if not step_counts:
            return 0
        if len(step_counts) is 1:
            return step_counts[0].step_number
        step_change = step_counts[0].step_number - step_counts[1].step_number
        if step_change < 0:
            return 0
        return step_change
    
    def is_sedentary_at(self, time):
        try:
            steps = self.get_step_count_at(time)
        except AntiSedentaryService.NoSteps:
            return False
        if steps < 150:
            return True
        else:
            return False

    def update(self, date):
        pass

    

class AntiSedentaryDecisionService(DecisionMessageService, DecisionContextService):

    MESSAGE_TEMPLATE_MODEL = AntiSedentaryMessageTemplate

    def __init__(self, decision):
        super().__init__(decision)
        self.__anti_sedentary_service = AntiSedentaryService(
            user = decision.user
        )

    def generate_context(self):
        context = super().generate_context()
        time_of_day_context = self.get_time_of_day_context()
        if time_of_day_context:
            context.append(time_of_day_context)
        return context

    def update_sedentary(self):
        pass

    def update_availability(self):
        if self.__anti_sedentary_service.can_randomize(self.decision.time):
            self.decision.available = True
            self.decision.save()
            super().update_availability()
        else:
            self.decision.available = False
            self.decision.save()

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