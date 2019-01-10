import pytz
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from behavioral_messages.models import MessageTemplate
from daily_tasks.models import DailyTask
from locations.services import LocationService
from randomization.models import Decision
from walking_suggestion_times.models import SuggestionTime

class Configuration(models.Model):
    user = models.ForeignKey(User)
    enabled = models.BooleanField(default=True)
    impute_context = models.BooleanField(default=False)

    service_initialized = models.BooleanField(default=False)

    day_start_hour = models.PositiveSmallIntegerField(default=6)
    day_start_minute = models.PositiveSmallIntegerField(default=0)
    day_end_hour = models.PositiveSmallIntegerField(default=21)
    day_end_minute = models.PositiveSmallIntegerField(default=0)

    @property
    def timezone(self):
        try:
            location_service = LocationService(self.user)
            return location_service.get_current_timezone()
        except LocationService.UnknownLocation:
            return pytz.utc

    def get_start_of_day(self, date):
        return datetime(
            year = date.year,
            month = date.month,
            day = date.day,
            hour = self.day_start_hour,
            minute = self.day_start_minute,
            tzinfo = self.timezone
        )

    def get_end_of_day(self, date):
        return datetime(
            year = date.year,
            month = date.month,
            day = date.day,
            hour = self.day_end_hour,
            minute = self.day_end_minute,
            tzinfo = self.timezone
        )

    def update_suggestion_times(self):
        for suggestion_time in SuggestionTime.objects.filter(user=self.user).all():
            self._update_suggestion_time_task(suggestion_time)

    def _update_suggestion_time_task(self, suggestion_time):
        daily_task, created = DailyTask.objects.get_or_create(
            user = suggestion_time.user,
            category = suggestion_time.category
        )
        if created:
            daily_task.create_task(
                task = 'walking_suggestions.tasks.start_decision',
                name = 'Walking suggestion %s for %s' % (suggestion_time.category, suggestion_time.user),
                arguments = {
                    'username': suggestion_time.user.username,
                    'category': suggestion_time.category
                }
            )
        task_start_time = self._get_task_start_time(suggestion_time)
        daily_task.set_time(
            hour = task_start_time['hour'],
            minute = task_start_time['minute']
        )

    def _get_task_start_time(self, suggestion_time):
        if not hasattr(settings, 'WALKING_SUGGESTION_TIME_OFFSET'):
            raise ImporperyConfigured("No walking suggestion time offset specified")
        now = datetime.now()
        time = datetime(now.year, now.month, now.day, suggestion_time.hour, suggestion_time.minute)
        time = time - timedelta(minutes=settings.WALKING_SUGGESTION_TIME_OFFSET)

        return {
            'hour': time.hour,
            'minute': time.minute
        }

class WalkingSuggestionDecision(Decision):
    pass

class WalkingSuggestionMessageTemplate(MessageTemplate):
    pass
