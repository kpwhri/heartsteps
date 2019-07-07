from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from daily_tasks.models import DailyTask
from days.models import Day

User = get_user_model()

class Configuration(models.Model):
    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    enabled = models.BooleanField(
        default = True
    )

    daily_task = models.ForeignKey(
        DailyTask,
        null = True,
        related_name = '+',
        on_delete = models.SET_NULL
    )

    hour = models.PositiveSmallIntegerField(
        null = True
    )
    minute = models.PositiveSmallIntegerField(
        null = True
    )

    def set_default_time(self):
        if hasattr(settings, 'ADHERENCE_UPDATE_TIME'):
            try:
                hour, minute = [int(piece) for piece in settings.ADHERENCE_UPDATE_TIME.split(':')]
                self.hour = hour
                self.minute = minute
            except:
                self.hour = None
                self.minute = None

    def update_daily_task(self):
        task = 'adherence_messages.tasks.update_adherence',
        task_name = 'Adherence update for %s' % (self.user.username)
        task_arguments = {
            'username': self.user.username
        }
        task_hour = self.hour
        task_minute = self.minute

        try:
            self.daily_task = DailyTask.objects.get(task__name=task_name)
            self.daily_task.update_task(
                task = task,
                name = task_name,
                arguments = task_arguments
            )
            self.daily_task.set_time(
                task_hour,
                task_minute
            )
        except DailyTask.DoesNotExist:
            self.daily_task = DailyTask.create_daily_task(
                user = self.user,
                category = None,
                task = task,
                name = task_name,
                arguments = task_arguments,
                hour = task_hour,
                minute = task_minute
            )


class DailyAdherenceMetric(models.Model):

    WORE_FITBIT = 'wore-fitbit'
    USED_APP = 'used-app'

    ADHERENCE_METRIC_CHOICES = [
        (WORE_FITBIT, 'Wore fitbit'),
        (USED_APP, 'Used app')
    ]

    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    day = models.ForeignKey(
        Day,
        related_name = '+',
        on_delete = models.CASCADE
    )
    category = models.CharField(
        max_length = 70,
        choices = ADHERENCE_METRIC_CHOICES
    )
    value = models.BooleanField(
        default = False
    )
