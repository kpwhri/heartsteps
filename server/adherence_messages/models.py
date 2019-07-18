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

from .signals import send_adherence_message as send_adherence_message_signal

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


class AdherenceMetric(models.Model):

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
        on_delete=models.CASCADE
    )
    date = models.DateField()
    category = models.CharField(
        max_length = 70,
        choices = ADHERENCE_METRIC_CHOICES
    )
    value = models.BooleanField(
        default = False
    )

    def __str__(self):
        return '%s: %s on %s' % (self.user.username, self.category, self.date.strftime('%Y-%m-%d'))

class AdherenceAlert(models.Model):

    class AdherenceMessageRecentlySent(RuntimeError):
        pass

    class AdherenceMessageBufferNotSet(ImproperlyConfigured):
        pass

    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    start = models.DateTimeField()
    end = models.DateTimeField(
        null = True
    )

    category = models.CharField(
        max_length = 70
    )

    def __str__(self):
        return '%s: %s' % (self.user.username, self.category)

    @property
    def active(self):
        if self.end:
            return False
        else:
            return True

    @property
    def duration(self):
        return timezone.now() - self.start

    @property
    def messages(self):
        return list(self.adherencemessage_set.all())

    def start_date(self):
        service = DayService(user = self.user)
        return service.get_date_at(self.start)

    def end_date(self):
        if self.end:
            service = DayService(user = self.user)
            return service.get_date_at(self.end)
        else:
            return None

    def send_adherence_message(self):
        send_adherence_message_signal.send(
            sender = AdherenceAlert,
            adherence_alert = self
        )

    def get_message_buffer_time(self):
        if hasattr(settings, 'ADHERENCE_MESSAGE_BUFFER_HOURS'):
            buffer_hours = settings.ADHERENCE_MESSAGE_BUFFER_HOURS
            return timezone.now() - timedelta(hours=int(buffer_hours))
        else:
            raise AdherenceAlert.AdherenceMessageBufferNotSet('Message buffer not set')

    def send_message(self, body):
        recently_sent_message_count = AdherenceMessage.objects.filter(
            adherence_alert__user = self.user,
            created__gte = self.get_message_buffer_time()
        ).count()

        if recently_sent_message_count > 0:
            raise AdherenceAlert.AdherenceMessageRecentlySent('Unable to send message')
        else:
            message = AdherenceMessage.objects.create(
                adherence_alert = self,
                body = body
            )
            message.send()

class AdherenceMessage(models.Model):
    adherence_alert = models.ForeignKey(
        AdherenceAlert,
        on_delete = models.CASCADE
    )
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
            service = SMSService(user = self.adherence_alert.user)
            self.message = service.send(self.body)
            self.save()
