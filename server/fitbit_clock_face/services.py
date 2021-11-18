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

    def get_step_count_query(self, start, end, created_before=None):
        queryset = StepCount.objects.filter(
            user = self.__user,
            start__gte = start,
            end__lte = end
        )
        if created_before:
            return queryset.filter(
                created__lte = created_before
            )
        else:
            return queryset

    def get_step_count_between(self, start, end, created_before=None):
        queryset = self.get_step_count_query(start, end, created_before)
        step_counts = [step_count.steps for step_count in queryset.all()]
        if not step_counts:
            raise StepCountService.NoStepCountRecorded('No steps')
        return sum(step_counts)

    def get_step_count_at(self, time):
        queryset = self.get_step_count_query(
            start = time - timedelta(minutes=5),
            end = time
        )
        step_count = queryset.last()
        if not step_count:
            raise StepCountService.NoStepCountRecorded('No step count at time')
        return step_count.steps 
