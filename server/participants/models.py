import json
import pytz
from datetime import datetime
from warnings import warn

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from daily_tasks.models import DailyTask
from days.models import Day
from days.services import DayService
from page_views.models import PageView
from sms_messages.models import (Contact, Message)

TASK_CATEGORY = 'PARTICIPANT_UPDATE'

class Study(models.Model):
    name = models.CharField(
        max_length = 75,
        unique = True
    )
    contact_name = models.CharField(
        max_length = 150,
        null = True
    )
    contact_number = models.CharField(
        max_length = 20,
        null = True
    )
    baseline_period = models.PositiveIntegerField(default=7)

    admins = models.ManyToManyField(User)

    def __str__(self):
        return self.name

class Cohort(models.Model):
    name = models.CharField(max_length=75)
    study = models.ForeignKey(
        Study,
        null = True,
        on_delete = models.CASCADE
    )

    def __str__(self):
        return self.name

class Participant(models.Model):
    """
    Represents a study participant

    When the participant is enrolled, a user is created.
    """
    heartsteps_id = models.CharField(
        primary_key=True,
        unique=True,
        max_length=25
    )
    enrollment_token = models.CharField(max_length=10, unique=True)
    birth_year = models.CharField(max_length=4, null=True, blank=True)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    cohort = models.ForeignKey(
        Cohort,
        null = True,
        on_delete = models.SET_NULL
    )

    active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

    class NotEnrolled(RuntimeError):
        pass

    def delete(self):
        if self.user:
            Day.objects.filter(user = self.user).delete()
            self.user.delete()
        super().delete()

    def enroll(self):
        user, created = User.objects.get_or_create(
            username = self.heartsteps_id
        )
        self.user = user
        self.save()

    @property
    def enrolled(self):
        if self.user:
            return True
        else:
            return False

    @property
    def date_joined(self):
        if self.user:
            return self.user.date_joined
        else:
            return None

    @property
    def is_active(self):
        return self.active

    @property
    def daily_task_name(self):
        return '%s daily update' % (self.user.username)

    @property
    def daily_task(self):
        try:
            return DailyTask.objects.get(
                user = self.user,
                category = TASK_CATEGORY
            )
        except DailyTask.DoesNotExist:
            return None

    def set_daily_task(self):
        if not hasattr(settings, 'PARTICIPANT_NIGHTLY_UPDATE_TIME'):
            raise ImproperlyConfigured('Participant nightly update time not configured')
        hour, minute = settings.PARTICIPANT_NIGHTLY_UPDATE_TIME.split(':')
        if not self.daily_task:
            self.__create_daily_task()
        self.daily_task.set_time(int(hour), int(minute))

    def __create_daily_task(self):
        task = DailyTask.objects.create(
            user = self.user,
            category = TASK_CATEGORY
        )
        task.create_task(
            task = 'participants.tasks.daily_update',
            name = self.daily_task_name,
            arguments = {
                'username': self.user.username
            }
        )
        return task

    def __str__(self):
        return self.heartsteps_id
