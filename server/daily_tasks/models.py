import pytz
import json
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from locations.services import LocationService

class DailyTask(models.Model):
    user = models.ForeignKey(User)
    category = models.CharField(max_length=20, null=True)
    task = models.ForeignKey(PeriodicTask, null=True)

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

    def create_daily_task(user, category, task, name, arguments, hour, minute):
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

    def set_time(self, hour, minute):
        self.hour = hour
        self.minute = minute
        self.save()

        try:
            location_service = LocationService(self.user)
            timezone = location_service.get_current_timezone()
        except LocationService.UnknownLocation:
            timezone = pytz.UTC

        time = datetime.now(timezone).replace(
            hour = hour,
            minute = minute
        )
        utc_time = time.astimezone(pytz.utc)
        self.task.crontab.hour = utc_time.hour
        self.task.crontab.minute = utc_time.minute
        self.task.crontab.save()

    def update_timezone(self):
        self.set_time(
            hour = self.hour,
            minute = self.minute
        )

    def delete_task(self):
        self.task.crontab.delete()
        self.task.delete()

    def get_next_run_time(self):
        pass
