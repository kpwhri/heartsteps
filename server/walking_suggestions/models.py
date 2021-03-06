import pytz
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from behavioral_messages.models import MessageTemplate
from daily_tasks.models import DailyTask
from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_api.services import FitbitService
from randomization.models import Decision
from randomization.models import DecisionContextQuerySet
from service_requests.models import ServiceRequest
from walking_suggestion_times.models import SuggestionTime

class Configuration(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    enabled = models.BooleanField(default=False)

    service_initialized_date = models.DateField(null=True)
    pooling = models.BooleanField(default=False)

    day_start_hour = models.PositiveSmallIntegerField(default=6)
    day_start_minute = models.PositiveSmallIntegerField(default=0)
    day_end_hour = models.PositiveSmallIntegerField(default=21)
    day_end_minute = models.PositiveSmallIntegerField(default=0)

    class SuggestionTimeDoesNotExist(RuntimeError):
        pass

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.suggestion_times:
            self.set_default_walking_suggestion_times()
        self.update_walking_suggestion_tasks()
    
    @property
    def service_initialized(self):
        if self.service_initialized_date is not None:
            return True
        else:
            return False

    @property
    def timezone(self):
        service = DayService(user=self.user)
        return service.get_current_timezone()

    @property
    def current_datetime(self):
        return timezone.now().astimezone(self.timezone)

    def get_start_of_day(self, day=None):
        if day:
            service = DayService(user=self.user)
            day = service.get_date_at(day)
        else:
            day = self.current_datetime
        return datetime(
            year = day.year,
            month = day.month,
            day = day.day,
            hour = self.day_start_hour,
            minute = self.day_start_minute,
            tzinfo = self.timezone
        )

    @property
    def fitbit_days_worn(self):
        try:
            fitbit_service = FitbitService(user = self.user)
        except FitbitService.NoAccount:
            return 0
        return FitbitDay.objects.filter(
            account = fitbit_service.account,
            wore_fitbit = True
        ).count()

    def get_end_of_day(self, day=None):
        dt = self.get_start_of_day(day=day)
        return dt.replace(
            hour = self.day_end_hour,
            minute = self.day_end_minute
        )
    
    def get_walking_suggestion_time(self, category, day):
        for suggestion_time in self.suggestion_times:
            if suggestion_time.category == category:
                return suggestion_time.get_datetime_on(day)
        raise Configuration.SuggestionTimeDoesNotExist('No suggestion time found')

    @property
    def suggestion_times(self):
        results = SuggestionTime.objects.filter(user=self.user).all()
        return list(results)

    def set_default_walking_suggestion_times(self):
        SuggestionTime.objects.filter(user=self.user).delete()

        suggestion_times = {
            SuggestionTime.MORNING: '8:30',
            SuggestionTime.LUNCH: '12:15',
            SuggestionTime.MIDAFTERNOON: '15:00',
            SuggestionTime.EVENING: '18:30',
            SuggestionTime.POSTDINNER: '21:00'
        }
        for category, time in suggestion_times.items():
            hour, minute = [int(x) for x in time.split(':')]
            SuggestionTime.objects.create(
                user = self.user,
                category = category,
                hour = hour,
                minute = minute
            )

    def __make_suggestion_time_task_category(self, category):
        return 'ws-%s' % (category)

    def __make_suggestion_time_task_name(self, category):
        return 'create-walking-suggestion-%s-%s' % (
            category,
            self.user.username
        )

    def __get_suggestion_time_task_arguments(self):
        return {
            'username': self.user.username
        }

    def __get_suggestion_time_task(self):
        return 'walking_suggestions.tasks.queue_walking_suggestion'

    def get_suggestion_time_task(self, category):
        try:
            daily_task = DailyTask.objects.get(
                user = self.user,
                category = self.__make_suggestion_time_task_category(category)
            )
        except DailyTask.DoesNotExist:
            daily_task = self.__create_suggestion_time_task(category)
        return daily_task

    def __create_suggestion_time_task(self, category):
        suggestion_time = SuggestionTime.objects.get(
            user = self.user,
            category = category
        )

        daily_task = DailyTask.create_daily_task(
            user = self.user,
            category = self.__make_suggestion_time_task_category(category),
            task = self.__get_suggestion_time_task(),
            name = self.__make_suggestion_time_task_name(category),
            arguments = self.__get_suggestion_time_task_arguments(),
            hour = suggestion_time.hour,
            minute = suggestion_time.minute
        )
        return daily_task

    def update_walking_suggestion_tasks(self):
        for suggestion_time in self.suggestion_times:
            daily_task = self.get_suggestion_time_task(
                category = suggestion_time.category
            )
            daily_task.update_task(
                task = self.__get_suggestion_time_task(),
                name = self.__make_suggestion_time_task_name(suggestion_time.category),
                arguments = self.__get_suggestion_time_task_arguments()
            )
            daily_task.set_time(
                hour = suggestion_time.hour,
                minute = suggestion_time.minute
            )
            if self.enabled:
                daily_task.enable()
            else:
                daily_task.disable()
        

class WalkingSuggestionMessageTemplate(MessageTemplate):
    pass

class WalkingSuggestionServiceRequest(ServiceRequest):
    pass

class WalkingSuggestionDecision(Decision):

    MESSAGE_TEMPLATE_MODEL = WalkingSuggestionMessageTemplate

    objects = DecisionContextQuerySet.as_manager()

    @property
    def sedentary_step_count(self):
        if hasattr(settings,'WALKING_SUGGESTION_DECISION_UNAVAILABLE_STEP_COUNT'):
            return int(settings.WALKING_SUGGESTION_DECISION_UNAVAILABLE_STEP_COUNT)
        return self.SEDENTARY_STEP_COUNT

    def get_sedentary_duration_minutes(self):
        if hasattr(settings,'WALKING_SUGGESTION_DECISION_WINDOW_MINUTES'):
            return int(settings.WALKING_SUGGESTION_DECISION_WINDOW_MINUTES)
        return self.SEDENTARY_DURATION_MINUTES

    def handle_no_step_count(self):
        pass

    @property
    def category(self):
        for tag in self.tags.all():
            if tag.tag in SuggestionTime.TIMES:
                return tag.tag
        return None

class NightlyUpdate(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    day = models.DateField()
    updated = models.BooleanField(default=False)

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day']

    @property
    def date(self):
        return self.day

class PoolingServiceConfiguration(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    use_pooling = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class PoolingServiceRequest(ServiceRequest):
    pass
