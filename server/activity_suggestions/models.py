import uuid, json, pytz
from datetime import datetime, timedelta

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User

from behavioral_messages.models import MessageTemplate
from locations.services import LocationService
from daily_tasks.models import DailyTask
from randomization.models import Decision, ContextTag

class SuggestionTime(models.Model):

    MORNING = 'morning'
    LUNCH = 'lunch'
    MIDAFTERNOON = 'midafternoon'
    EVENING = 'evening'
    POSTDINNER = 'postdinner'

    TIMES = [MORNING, LUNCH, MIDAFTERNOON, EVENING, POSTDINNER]

    CATEGORIES = [
        (MORNING, 'Morning'),
        (LUNCH, 'Lunch'),
        (MIDAFTERNOON, 'Afternoon'),
        (EVENING, 'Evening'),
        (POSTDINNER, 'Post dinner')
    ]

    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)

    user = models.ForeignKey(User)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    hour = models.PositiveSmallIntegerField()
    minute = models.PositiveSmallIntegerField()

    def get_task_start_time(self):
        if not hasattr(settings, 'ACTIVITY_SUGGESTION_TIME_OFFSET'):
            raise ImporperyConfigured("No activity suggestion time offset specified")
        now = datetime.now()
        time = datetime(now.year, now.month, now.day, self.hour, self.minute)
        time = time - timedelta(minutes=settings.ACTIVITY_SUGGESTION_TIME_OFFSET)

        return {
            'hour': time.hour,
            'minute': time.minute
        }

    def update_daily_task(self):
        daily_task, created = DailyTask.objects.get_or_create(
            user = self.user,
            category = self.category
        )
        if created:
            daily_task.create_task(
                task = 'activity_suggestions.tasks.start_decision',
                name = 'Activity suggestion %s for %s' % (self.category, self.user),
                arguments = {
                    'username': self.user.username,
                    'category': self.category
                }
            )
        task_start_time = self.get_task_start_time()
        daily_task.set_time(
            hour = task_start_time['hour'],
            minute = task_start_time['minute']
        )

    def __str__(self):
        return "%s:%s (%s) - %s" % (self.hour, self.minute, self.type, self.configuration.user)         

class Configuration(models.Model):
    user = models.ForeignKey(User)
    enabled = models.BooleanField(default=False)

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

class ActivitySuggestionMessageTemplate(MessageTemplate):
    pass

class ActivitySuggestionDecision(Decision):
    pass
