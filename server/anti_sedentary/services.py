from datetime import datetime, timedelta

from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from days.services import DayService
from fitbit_activities.services import FitbitStepCountService
from fitbit_api.services import FitbitService
from randomization.services import DecisionMessageService, DecisionContextService
from walking_suggestion_times.models import SuggestionTime
from watch_app.services import StepCountService

from anti_sedentary.clients import AntiSedentaryClient
from anti_sedentary.models import AntiSedentaryDecision, AntiSedentaryMessageTemplate, Configuration

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
            decision = AntiSedentaryDecision.objects.create(
                user = self.__user,
                time = time,
                imputed = True,
                treated = False
            )
            decision.sedentary = decision.is_sedentary()
            decision.save()
            return decision

    def is_sedentary_at(self, time):
        service = StepCountService(user = self.__user)
        try:
            steps = service.get_step_count_between(
                start = time - timedelta(minutes=40),
                end = time
            )
        except StepCountService.NoStepCountRecorded:
            return False
        if steps < AntiSedentaryDecision.SEDENTARY_STEP_COUNT:
            return True
        else:
            return False   

    def decide(self, decision):
        if self._client:
            return self._client.decide(
                decision = decision,
                step_count = self.get_step_count_change_at(decision.time),
                time = self.localize_time(decision.time),
                day_start = self.get_day_start(decision.time),
                day_end = self.get_day_end(decision.time)
            )
        else:
            return decision.decide()

    def localize_time(self, time):
        service = DayService(self.__user)
        local_timezone = service.get_timezone_at(time)
        return time.astimezone(local_timezone)

    def get_day_end(self, time):
        local_time = self.localize_time(time)
        try:
            suggestion_time = SuggestionTime.objects.get(
                user=self.__user,
                category = SuggestionTime.POSTDINNER
            )
        except SuggestionTime.DoesNotExist:
            return local_time.replace(hour=20, minute=0)
        updated_time = local_time.replace(
            hour = suggestion_time.hour,
            minute = suggestion_time.minute
        )
        return updated_time + timedelta(hours=1)


    def get_day_start(self, time):
        end_time = self.get_day_end(time)
        return end_time - timedelta(hours=12)

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
        service = StepCountService(user = self.__user)
        try:
            return service.get_step_count_between(
                start = time - timedelta(minutes=40),
                end = time
            )
        except StepCountService.NoStepCountRecorded:
            raise AntiSedentaryService.NoSteps('No steps')

    def get_step_count_change_at(self, time):
        service = StepCountService(user = self.__user)
        try:
            return service.get_step_count_at(time)
        except StepCountService.NoStepCountRecorded:
            return 0

    def update(self, date):
        if not self._client:
            raise AntiSedentaryService.Unavailable('No client')

        decision_times = []
        day_start = self.get_day_start(date)
        day_end = self.get_day_end(date)

        steps_service = FitbitStepCountService(
            user = self.__user
        )

        decision_interval = self.decision_minute_interval
        current_time = day_start
        while current_time <= day_end:
            decision = self.get_decision(time = current_time)
            decision_times.append({
                'id': str(decision.id),
                'time': current_time,
                'sedentary': decision.is_sedentary(),
                'steps': decision.get_sedentary_step_count()
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

    def get_time_of_day_context(self):
        service = DayService(user = self.decision.user)
        local_timezone = service.get_timezone_at(self.decision.time)
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