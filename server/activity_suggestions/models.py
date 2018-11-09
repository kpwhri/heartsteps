import uuid, json, pytz
from datetime import datetime, timedelta

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User

from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule

from locations.services import LocationService
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

    def next_suggestion_time(self, timezone):
        if not hasattr(settings, 'ACTIVITY_SUGGESTION_TIME_OFFSET'):
            raise ImporperyConfigured("No activity suggestion time offset specified")
        now = datetime.now().astimezone(timezone)
        time = datetime(now.year, now.month, now.day, self.hour, self.minute, tzinfo=timezone)
        time = time - timedelta(minutes=settings.ACTIVITY_SUGGESTION_TIME_OFFSET)
        if now < time:
            return time + timedelta(days=1)
        else:
            return time

    def __str__(self):
        return "%s:%s (%s) - %s" % (self.hour, self.minute, self.type, self.configuration.user)         

class Configuration(models.Model):

    NIGHTLY_TASK_CATEGORY = 'nightly update'

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

    def update_daily_tasks(self):
        for suggestion_time in SuggestionTime.objects.filter(user=self.user).all():
            self.update_suggestion_time_task(suggestion_time)
        try:
            daily_task = DailyTask.objects.get(
                configuration = self,
                category = self.NIGHTLY_TASK_CATEGORY
            )
        except DailyTask.DoesNotExist:
            daily_task = self.create_nightly_task()
        if not hasattr(settings, 'ACTIVITY_SUGGESTION_UPDATE_TIME'):
            raise ImporperyConfigured("No activity suggestion update time set")
        parsed_time = settings.ACTIVITY_SUGGESTION_UPDATE_TIME.split(':')
        daily_task.set_time(int(parsed_time[0]), int(parsed_time[1]), self.timezone)

    def update_suggestion_time_task(self, suggestion_time):
        daily_task, created = DailyTask.objects.get_or_create(
            configuration = self,
            category = suggestion_time.category
        )
        if created:
            daily_task.create_task(
                task = 'activity_suggestions.tasks.start_decision',
                name = 'Activity suggestion %s for %s' % (suggestion_time.category, self.user),
                arguments = {
                    'username': self.user.username,
                    'category': suggestion_time.category
                }
            )
        next_time = suggestion_time.next_suggestion_time(self.timezone)
        daily_task.set_time(
            hour = next_time.hour,
            minute = next_time.minute,
            timezone = self.timezone
        )

    def create_nightly_task(self):
        daily_task = DailyTask.objects.create(
            configuration = self,
            category = self.NIGHTLY_TASK_CATEGORY
        )
        daily_task.create_task(
            task = 'activity_suggestions.tasks.update_activity_suggestion_service',
            name = 'Activity suggestion nightly update for %s' % self.user,
            arguments = {
                'username': self.user.username
            }
        )
        return daily_task

    def __str__(self):
        if self.enabled:
            return "%s Enabled" % self.user
        else:
            return "%s Disabled" % self.user

class DailyTask(models.Model):
    configuration = models.ForeignKey(Configuration)
    category = models.CharField(max_length=20)
    task = models.ForeignKey(PeriodicTask, null=True)

    def create_task(self, task, name, arguments):
        self.task = PeriodicTask.objects.create(
            crontab = CrontabSchedule.objects.create(),
            name = name,
            task = task,
            kwargs = json.dumps(arguments)
        )
        self.save()

    def set_time(self, hour, minute, timezone):
        time = datetime.now(timezone).replace(
            hour = hour,
            minute = minute
        )
        utc_time = time.astimezone(pytz.utc)
        self.task.crontab.hour = utc_time.hour
        self.task.crontab.minute = utc_time.minute
        self.task.crontab.save()
        PeriodicTasks.changed(self.task)

    def delete_task():
        self.task.crontab.delete()
        self.task.delete()

class ActivitySuggestionDecisionManager(models.Manager):

    def get_queryset(self):
        return Decision.objects.filter(tags__tag="activity suggestion")

class ActivitySuggestionDecision(Decision):
    objects = ActivitySuggestionDecisionManager()

    class Meta:
        proxy = True

class ServiceRequest(models.Model):
    user = models.ForeignKey(User)
    url = models.CharField(max_length=150)

    request_data = models.TextField()
    request_time = models.DateTimeField()

    response_code = models.IntegerField()
    response_data = models.TextField()
    response_time = models.DateTimeField()

    def __str__(self):
        return "%s (%d) %s" % (self.user, self.response_code, self.url)