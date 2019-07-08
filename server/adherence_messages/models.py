from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from daily_tasks.models import DailyTask
from days.models import Day
from days.services import DayService

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
        if self.enabled:
            self.daily_task.enable()
        else:
            self.daily_task.disable()

class AdherenceDay(models.Model):

    class MetricNotFound(RuntimeError):
        pass

    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    date = models.DateField()

    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    def get_metric(self, category):
        metric = self.dailyadherencemetric_set.filter(
            category = category
        ).first()
        if metric:
            return metric.value
        else:
            raise self.MetricNotFound('%s not found for %s on %s' % (
                category,
                self.user.username,
                self.date
            ))

    def set_metric(self, category, value):
        DailyAdherenceMetric.objects.update_or_create(
            adherence_day = self,
            category = category,
            defaults = {
                'value': value
            }
        )

    def get_app_installed(self):
        return self.get_metric(DailyAdherenceMetric.APP_INSTALLED)

    def set_app_installed(self, value):
        self.set_metric(DailyAdherenceMetric.APP_INSTALLED, value)

    app_installed = property(get_app_installed, set_app_installed)

    def get_app_used(self):
        return self.get_metric(DailyAdherenceMetric.APP_USED)
    
    def set_app_used(self, value):
        return self.set_metric(DailyAdherenceMetric.APP_USED, value)

    app_used = property(get_app_used, set_app_used)


class DailyAdherenceMetric(models.Model):

    WORE_FITBIT = 'wore-fitbit'
    APP_USED = 'app-used'
    APP_INSTALLED = 'app-installed'

    ADHERENCE_METRIC_CHOICES = [
        (WORE_FITBIT, 'Wore fitbit'),
        (APP_USED, 'Used app'),
        (APP_INSTALLED, 'Installed app')
    ]

    adherence_day = models.ForeignKey(
        AdherenceDay,
        null = True,
        on_delete = models.CASCADE
    )
    category = models.CharField(
        max_length = 70,
        choices = ADHERENCE_METRIC_CHOICES
    )
    value = models.BooleanField(
        default = False
    )

class AdherenceMessage(models.Model):
    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    adherence_day = models.ForeignKey(
        AdherenceDay,
        related_name = '+',
        null = True,
        on_delete = models.SET_NULL
    )
    category = models.CharField(
        max_length = 70,
        null = True
    )
    body = models.TextField(
        null = True
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def send(self):
        pass
