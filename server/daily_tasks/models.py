import pytz
import json
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from locations.services import LocationService

DAYS_OF_WEEK = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday'
]

CRON_DAYS_OF_WEEK = [
    'sunday',
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday'
]

class DailyTask(models.Model):
    user = models.ForeignKey(User)
    category = models.CharField(max_length=20, null=True)
    task = models.ForeignKey(PeriodicTask, null=True)

    day = models.CharField(max_length=15, null=True)
    hour = models.IntegerField(null=True)
    minute = models.IntegerField(null=True)

    def __str__(self):
        if self.task:
            return self.task.name
        else:
            return "%s (no task)" % (self.user)

    @property
    def enabled(self):
        return self.task.enabled

    def enable(self):
        if not self.enabled:
            self.task.enabled = True
            self.task.save()

    def disable(self):
        if self.enabled:
            self.task.enabled = False
            self.task.save()

    @property
    def timezone(self):
        try:
            location_service = LocationService(self.user)
            return location_service.get_current_timezone()
        except LocationService.UnknownLocation:
            return pytz.UTC

    def create_daily_task(user, category, task, name, arguments, hour, minute, day=None):
        daily_task = DailyTask.objects.create(
            user = user,
            category = category
        )
        daily_task.create_task(
            task = task,
            name = name,
            arguments = arguments
        )
        daily_task.set_time(
            day = day,
            hour = hour,
            minute = minute
        )
        return daily_task

    def create_task(self, task, name, arguments):
        self.task = PeriodicTask.objects.create(
            crontab = CrontabSchedule.objects.create(),
            name = name,
            task = task,
            kwargs = json.dumps(arguments)
        )
        self.save()

    def set_time(self, hour, minute, day=None):
        self.day = day
        self.hour = hour
        self.minute = minute
        self.save()

        time = datetime.now(self.timezone).replace(
            hour = hour,
            minute = minute
        )
        utc_time = time.astimezone(pytz.utc)
        self.task.crontab.hour = utc_time.hour
        self.task.crontab.minute = utc_time.minute
        if self.day:
            self.task.crontab.day = CRON_DAYS_OF_WEEK.index(self.day)
        else:
            self.task.crontab.day = '*'
        self.task.crontab.save()

    def update_timezone(self):
        self.set_time(
            hour = self.hour,
            minute = self.minute
        )

    def delete_task(self):
        if self.task:
            self.task.crontab.delete()
            self.task.delete()

    def get_next_run_time(self):
        if not self.enabled:
            return None
        location_service = LocationService(self.user)
        now = timezone.now().astimezone(self.timezone)
        next_run = datetime(now.year, now.month, now.day, self.hour, self.minute, tzinfo=now.tzinfo)

        if self.day:
            current_day_of_week = now.weekday()
            reflection_day_of_week = DAYS_OF_WEEK.index(self.day)
            days_offset = reflection_day_of_week - current_day_of_week
            next_run = next_run + timedelta(days=days_offset)

        if next_run < now:
            if self.day:
                return next_run + timedelta(days=7)
            else:
                return next_run + timedelta(days=1)
        else:
            return next_run
