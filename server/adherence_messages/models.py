from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from daily_tasks.models import DailyTask
from days.models import Day
from days.services import DayService
from sms_messages.models import Message
from sms_messages.services import SMSService

User = get_user_model()

class Configuration(models.Model):
    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    daily_task = models.ForeignKey(
        DailyTask,
        null = True,
        related_name = '+',
        on_delete = models.SET_NULL
    )

    enabled = models.BooleanField(
        default = True
    )
    hour = models.PositiveSmallIntegerField(
        null = True
    )
    minute = models.PositiveSmallIntegerField(
        null = True
    )

    created = models.DateTimeField(
        auto_now_add = True
    )
    updated = models.DateTimeField(
        auto_now = True
    )

    def __str__(self):
        if self.enabled:
            return '%s (enabled)' % (self.user.username)
        else:
            return '%s (disabled)' % (self.user.username)

    def set_default_time(self):
        if hasattr(settings, 'ADHERENCE_MESSAGE_TIME'):
            try:
                hour, minute = [int(piece) for piece in settings.ADHERENCE_MESSAGE_TIME.split(':')]
                self.hour = hour
                self.minute = minute
            except:
                self.hour = None
                self.minute = None

    def update_daily_task(self):
        task = 'adherence_messages.tasks.send_adherence_message',
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
        if self.enabled:
            self.daily_task.enable()
        else:
            self.daily_task.disable()

class AdherenceBase(models.Model):

    WORE_FITBIT = 'wore-fitbit'
    APP_USED = 'app-used'
    APP_INSTALLED = 'app-installed'

    ADHERENCE_METRIC_CHOICES = [
        (WORE_FITBIT, 'Wore fitbit'),
        (APP_USED, 'Used app'),
        (APP_INSTALLED, 'Installed app')
    ]

    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    category = models.CharField(
        max_length = 70,
        choices = ADHERENCE_METRIC_CHOICES,
        null = True
    )

    class Meta:
        abstract = True


class AdherenceMetric(AdherenceBase):

    date = models.DateField()
    value = models.BooleanField(
        default = False
    )

    def __str__(self):
        return '%s: %s on %s' % (self.user.username, self.category, self.date.strftime('%Y-%m-%d'))

class AdherenceMessage(AdherenceBase):

    message = models.ForeignKey(
        Message,
        null = True,
        on_delete = models.SET_NULL
    )
    body = models.TextField(
        null = True
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def send(self):
        if not self.message:
            service = SMSService(user = self.user)
            self.message = service.send(self.body)
            self.save()
