import pytz
import json
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from days.services import DayService

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
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE
        )
    category = models.CharField(max_length=20, null=True)
    task = models.ForeignKey(
        PeriodicTask,
        null=True,
        on_delete = models.CASCADE
        )

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
        service = DayService(user=self.user)
        return service.get_current_timezone()

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
        try:
            self.task = PeriodicTask.objects.get(name=name)
        except PeriodicTask.DoesNotExist:
            self.task = PeriodicTask(name=name)
        if not self.task.crontab:
            crontab = CrontabSchedule.objects.create()
            self.task.crontab = crontab
        self.task.task = task
        self.task.kwargs = json.dumps(arguments)
        self.task.save()
        self.save()

    def update_task(self, task, name, arguments):
        self.task.task = task
        self.task.name = name
        self.task.kwargs = json.dumps(arguments)
        self.task.save()

    def set_time(self, hour, minute, day=None):
        time = datetime.now(self.timezone).replace(
            hour = hour,
            minute = minute
        )
        if day:
            day_offset = time.weekday() - DAYS_OF_WEEK.index(day)
            time = time - timedelta(days=day_offset)
        utc_time = time.astimezone(pytz.utc)
        self.task.crontab.hour = utc_time.hour
        self.task.crontab.minute = utc_time.minute
        if day:
            utc_day = DAYS_OF_WEEK[utc_time.weekday()]
            self.task.crontab.day_of_week = CRON_DAYS_OF_WEEK.index(utc_day)
        else:
            self.task.crontab.day_of_week = '*'
        self.task.crontab.save()
        self.task.save()

        self.day = day
        self.hour = hour
        self.minute = minute
        self.save()

    def update_timezone(self):
        self.set_time(
            hour = self.hour,
            minute = self.minute,
            day = self.day
        )

    def delete_task(self):
        try:
            if self.task:
                self.task.crontab.delete()
                self.task.delete()
        except PeriodicTask.DoesNotExist:
            pass

    def get_next_run_time(self):
        if not self.enabled:
            return None
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
