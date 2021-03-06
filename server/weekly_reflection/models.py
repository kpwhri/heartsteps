from datetime import timedelta

from django.utils import timezone

from django.db import models
from django.contrib.auth import get_user_model

from daily_tasks.models import DailyTask

User = get_user_model()

DAYS_OF_WEEK = [
    'saturday',
    'sunday'
]

DAYS_OF_WEEK_NAMES = [
    'Saturday',
    'Sunday'
]

DAYS_OF_WEEK_CHOICES = zip(DAYS_OF_WEEK, DAYS_OF_WEEK_NAMES)

class ReflectionTime(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK_CHOICES)
    time = models.CharField(max_length=15)

    active = models.BooleanField(default=True)
    daily_task = models.ForeignKey(DailyTask, null=True, on_delete = models.SET_NULL)

    def __str__(self):
        if self.active:
            return "%s at %s (%s)" % (self.day, self.time, self.user)
        else:
            return "Inactive (%s)" % (self.user)

    def save(self, *args, **kwargs):
        if not self.daily_task:
            self.create_daily_task()
        else:
            self.update_daily_task()
        if self.active:
            self.daily_task.enable()
        else:
            self.daily_task.disable()
        super().save(*args, **kwargs)

    def create_daily_task(self):
        task_name = 'weekly reflection for %s' % (self.user.username)
        try:
            self.daily_task = DailyTask.objects.get(task__name=task_name)
        except DailyTask.DoesNotExist:
            self.daily_task = DailyTask.create_daily_task(
                user = self.user,
                category = None,
                task = 'weekly_reflection.tasks.send_reflection',
                name = task_name,
                arguments = {
                    'username': self.user.username
                },
                day = self.day,
                hour = self.hour,
                minute = self.minute
            )

    def update_daily_task(self):
        self.daily_task.set_time(
            day = self.day,
            hour = self.hour,
            minute = self.minute
        )

    @property
    def formatted_time(self):
        if self.day and self.time:
            return "%s at %s" % (self.day_name, self.time)
        else:
            return "Unset"
            
    @property
    def day_name(self):
        try:
            index = DAYS_OF_WEEK.index(self.day)
            return DAYS_OF_WEEK_NAMES[index]
        except ValueError:
            return self.day

    @property
    def hour(self):
        return int(self.time.split(':')[0])

    @property
    def minute(self):
        return int(self.time.split(':')[1])

    def get_next_time(self):
        return self.daily_task.get_next_run_time()
