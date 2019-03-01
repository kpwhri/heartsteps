from datetime import datetime, timedelta

from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from anti_seds.models import StepCount
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_api.services import FitbitService
from locations.services import LocationService
from randomization.services import DecisionMessageService, DecisionContextService

from anti_sedentary.clients import AntiSedentaryClient
from anti_sedentary.models import AntiSedentaryDecision, AntiSedentaryMessageTemplate, Configuration

class FitbitStepCountService:

    def __init__(self, user, date):
        self.user = user
        self.date = date
        
        self.fitbit_account = FitbitService.get_account(user)

    def get_step_count_between(self, start, end):
        step_counts = FitbitMinuteStepCount.objects.filter(
            account = self.fitbit_account,
            time__range = [start, end]
        ).all()
        total_steps = 0
        for step_count in step_counts:
            total_steps += step_count.steps
        return total_steps

    def is_sedentary_at(self, time):
        step_count = self.get_step_count_between(
            start = time - timedelta(minutes=40),
            end = time
        )
        return False

    def steps_at(self, time):
        return self.get_step_count_between(
            start = time - timedelta(minutes=5),
            end = time
        )

class AntiSedentaryService:

    class Unavailable(ImproperlyConfigured):
        pass

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
            pass
        if not configuration:
            raise AntiSedentaryService.NoConfiguration('No configuration')
        self.__configuration = configuration
        self.__user = configuration.user

        if hasattr(settings, 'ANTI_SEDENTARY_DECISION_MINUTE_INTERVAL'):
            self.decision_minute_interval = settings.ANTI_SEDENTARY_DECISION_MINUTE_INTERVAL
        else:
            raise ImproperlyConfigured('No decision minute interval set')

        try:
            self._client = AntiSedentaryClient(
                user = self.__user
            )
        except AntiSedentaryClient.NoConfiguration:
            self._client = None

    def create_decision(self, test=False):
        decision = AntiSedentaryDecision.objects.create(
            user = self.__user,
            time = timezone.now(),
            test = test
        )
        return decision
    
    def get_decision(self, time):
        try:
            delta = timedelta(minutes=self.decision_minute_interval) - timedelta(seconds=1)
            return AntiSedentaryDecision.objects.get(
                user = self.__user,
                test = False,
                time__range = [
                    time - delta,
                    time
                ]
            )
        except AntiSedentaryDecision.DoesNotExist:
            return AntiSedentaryDecision.objects.create(
                user = self.__user,
                time = time,
                imputed = True,
                available = False
            )

    def decide(self, decision):
        if self._client:
            return self._client.decide(
                decision = decision,
                step_count = self.get_step_count_change_at(decision.time),
                day_start = self.get_day_start(decision.time),
                day_end = self.get_day_end(decision.time)
            )
        else:
            return decision.decide()

    def get_day_end(self, time):
        location_service = LocationService(self.__user)
        local_timezone = location_service.get_timezone_on(time)
        local_time = time.astimezone(local_timezone)

        return local_time.replace(hour=20, minute=0)

    def get_day_start(self, time):
        location_service = LocationService(self.__user)
        local_timezone = location_service.get_timezone_on(time)
        local_time = time.astimezone(local_timezone)

        return local_time.replace(hour=8, minute=0)

    def time_within_day(self, time):
        end_of_day = self.get_day_end(time)
        start_of_day = self.get_day_start(time)

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
        if not self._client:
            raise AntiSedentaryService.Unavailable('No client')

        decision_times = []
        day_start = self.get_day_start(date)
        day_end = self.get_day_end(date)

        steps_service = FitbitStepCountService(
            user = self.__user,
            date = date
        )

        decision_interval = self.decision_minute_interval
        current_time = day_start
        while current_time <= day_end:
            decision = self.get_decision(time = current_time)
            decision_times.append({
                'id': str(decision.id),
                'time': current_time,
                'sedentary': steps_service.is_sedentary_at(current_time),
                'steps': steps_service.steps_at(current_time)
            })
            current_time = current_time + timedelta(minutes=decision_interval)

        self._client.update(
            decisions = decision_times,
            day_start = day_start,
            day_end = day_end
        )

    

class AntiSedentaryDecisionService(DecisionMessageService, DecisionContextService):

    MESSAGE_TEMPLATE_MODEL = AntiSedentaryMessageTemplate

    def __init__(self, decision):
        super().__init__(decision)
        self.__anti_sedentary_service = AntiSedentaryService(
            user = self.decision.user
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
    
    def decide(self):
        if self.decision.test:
            return self.decision.decide()
        else:
            return self.__anti_sedentary_service.decide(self.decision)