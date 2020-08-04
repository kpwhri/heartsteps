import json
import pytz
from datetime import datetime
from datetime import timedelta
from warnings import warn

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from slugify import slugify

from daily_tasks.models import DailyTask
from days.models import Day
from days.services import DayService
from days.services import TimezoneService
from fitbit_api.models import FitbitAccountUser
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

    @property
    def slug(self):
        return slugify(self.name)

    def __str__(self):
        return self.name

class Cohort(models.Model):
    name = models.CharField(max_length=75)
    study = models.ForeignKey(
        Study,
        null = True,
        on_delete = models.CASCADE
    )

    study_length = models.PositiveIntegerField(
        null = True
    )

    def get_daily_timezones(self, start, end):
        participants = Participant.objects.filter(cohort=self) \
            .exclude(
                archived = True,
                user = None
            ).all()
        return TimezoneService.get_timezones(
            users = [p.user for p in participants if p.user],
            start = start,
            end = end
        )
    
    @property
    def slug(self):
        return slugify(self.name)

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

    study_start_date = models.DateField(
        null = True
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
    def fitbit_account(self):
        if not hasattr(self, '_fitbit_account'):
            if self.user:
                try:
                    fitbit_account_user = FitbitAccountUser.objects.prefetch_related('account').get(user = self.user)
                    self._fitbit_account = fitbit_account_user.account
                except FitbitAccountUser.DoesNotExist:
                    self._fitbit_account = None
            else:
                self._fitbit_account = None
        return self._fitbit_account

    def get_study_start_datetime(self):
        if self.fitbit_account and self.fitbit_account.first_updated:
            return self.fitbit_account.first_updated
        else:
            return None
    
    def get_study_start_date(self):
        study_start_datetime = self.get_study_start_datetime()
        if study_start_datetime:
            day_service = DayService(user = self.user)
            return day_service.get_date_at(study_start_datetime)
        else:
            return None

    @property
    def study_start(self):
        if self.user:            
            day_service = DayService(user = self.user)
            if self.study_start_date:
                return service.get_start_of_day(self.study_start_date)
            else:
                study_start_datetime = self.get_study_start_datetime()
                if study_start_datetime:
                    return day_service.get_start_of_day(study_start_datetime)
        return None

    @property
    def study_end(self):
        if self.user:
            service = DayService(user = self.user)
            end_date = self.date_joined + timedelta(days=self.study_length)
            return service.get_end_of_day(end_date)
        return self.date_joined

    @property
    def study_length(self):
        if self.cohort and self.cohort.study_length:
            return self.cohort.study_length
        else:
            return 30

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

class DataExport(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE
    )

    filename = models.CharField(max_length=150)
    start = models.DateTimeField()
    end = models.DateTimeField()

    error_message = models.TextField(
        null = True
    )

    def __str__(self):
        return self.filename
