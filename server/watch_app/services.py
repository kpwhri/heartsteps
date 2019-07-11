from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured

from .models import StepCount
from .models import User

class StepCountService:

    class NoUser(ImproperlyConfigured):
        pass

    class NoStepCountRecorded(RuntimeError):
        pass

    def __init__(self, user=None, username=None):
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
        if not user:
            raise self.NoUser('No user')
        self.__user = user

    def get_step_count_between(self, start, end):
        step_counts = StepCount.objects.filter(
            user = self.__user,
            start__gte=start,
            end__lte=end
        ).all()
        step_counts = list(step_counts)
        if not step_counts:
            raise StepCountService.NoStepCountRecorded('No steps')
        total_steps = 0
        for step_count in step_counts:
            total_steps += step_count.steps
        return total_steps

    def get_step_count_at(self, time):
        step_count = StepCount.objects.filter(
            user = self.__user,
            start__gte = time - timedelta(minutes=5),
            end__lte = time
        ).last()
        if not step_count:
            raise StepCountService.NoStepCountRecorded('No step count at time')
        return step_count.steps 
