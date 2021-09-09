import json
from django.core.exceptions import ImproperlyConfigured, ValidationError
import pytz
from datetime import datetime
from datetime import timedelta
from warnings import warn

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from slugify import slugify

from daily_tasks.models import DailyTask
from days.models import Day
from days.services import DayService
from days.services import TimezoneService
from fitbit_api.models import FitbitAccountUser
from page_views.models import PageView
from sms_messages.models import (Contact, Message)

TASK_CATEGORY = 'PARTICIPANT_UPDATE'

User = get_user_model()


class Study(models.Model):
    class Meta:
        verbose_name = 'Study'
        verbose_name_plural = 'Studies'

    name = models.CharField(
        max_length=75,
        unique=True,
        blank=True
    )
    contact_name = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )
    contact_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    baseline_period = models.PositiveIntegerField(default=7)
    studywide_feature_flags = models.TextField(default="", blank=True)

    admins = models.ManyToManyField(User)

    def clean_fields(self, exclude=['contact_name', 'contact_number']):
        super().clean_fields(exclude=exclude)
        raise_error = False
        studywide_feature_flags_list = self.studywide_feature_flags.split(
            ", ")
        cohorts = Cohort.objects.filter(study=self)
        for cohort in cohorts:
            cohort_feature_flags_list = cohort.cohort_feature_flags.split(", ")
            for cohort_flag in cohort_feature_flags_list:
                if cohort_flag in studywide_feature_flags_list and cohort_flag != '__all__':
                    raise_error = True
                    # raise ValidationError(
                    #     'Cannot add flag because it is already a study feature flag')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Study, self).save(*args, **kwargs)

    @property
    def slug(self):
        return slugify(self.name)

    def __str__(self):
        return self.name


class Cohort(models.Model):
    name = models.CharField(max_length=75, blank=True)
    study = models.ForeignKey(
        Study,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    study_length = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    export_data = models.BooleanField(default=False)
    export_bucket_url = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )
    cohort_feature_flags = models.TextField(default="", blank=True)

    def clean_fields(self, exclude=['study_length', 'export_bucket_url']):
        super().clean_fields(exclude=exclude)
        raise_error = False
        if not self.study:
            return
        studywide_feature_flags_list = self.study.studywide_feature_flags.split(
            ", ")
        cohort_feature_flags_list = self.cohort_feature_flags.split(", ")
        for cohort_flag in cohort_feature_flags_list:
            if cohort_flag in studywide_feature_flags_list and cohort_flag != '__all__':
                raise_error = True
                # raise ValidationError(
                # 'Cannot add flag because it is already a study feature flag')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Cohort, self).save(*args, **kwargs)

    def get_daily_timezones(self, start, end):
        participants = Participant.objects.filter(cohort=self) \
            .exclude(
                archived=True,
                user=None
        ).all()
        return TimezoneService.get_timezones(
            users=[p.user for p in participants if p.user],
            start=start,
            end=end
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

    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE)
    cohort = models.ForeignKey(
        Cohort,
        null=True,
        on_delete=models.SET_NULL
    )

    study_start_date = models.DateField(
        null=True
    )

    active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

    class NotEnrolled(RuntimeError):
        pass

    def delete(self):
        if self.user:
            Day.objects.filter(user=self.user).delete()
            self.user.delete()
        super().delete()

    def enroll(self):
        user, created = User.objects.get_or_create(
            username=self.heartsteps_id
        )
        self.user = user
        if self.study_start_date is None:
            self.study_start_date = self.get_study_start_date()
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
                    fitbit_account_user = FitbitAccountUser.objects.prefetch_related(
                        'account').get(user=self.user)
                    self._fitbit_account = fitbit_account_user.account
                except FitbitAccountUser.DoesNotExist:
                    self._fitbit_account = None
            else:
                self._fitbit_account = None
        return self._fitbit_account

    def get_fitbit_start_datetime(self):
        if self.fitbit_account and self.fitbit_account.first_updated:
            return self.fitbit_account.first_updated
        else:
            return None

    def get_study_start_date(self):
        if self.user and self.user.date_joined:
            study_start_datetime = self.user.date_joined
        else:
            study_start_datetime = self.get_fitbit_start_datetime()
        if study_start_datetime:
            day_service = DayService(user=self.user)
            return day_service.get_date_at(study_start_datetime)
        else:
            return None

    def get_study_start_datetime(self):
        study_start_date = self.get_study_start_date()
        if study_start_date:
            day_service = DayService(user=self.user)
            return day_service.get_start_of_day(study_start_date)
        return None

    def get_study_end_datetime(self):
        study_start_date = self.get_study_start_date()
        if study_start_date and self.study_length:
            end_date = self.study_start + timedelta(days=self.study_length)
            service = DayService(user=self.user)
            return service.get_end_of_day(end_date)
        else:
            return None

    @property
    def study_start(self):
        if not hasattr(self, '_study_start'):
            self._study_start = self.get_study_start_datetime()
        return self._study_start

    @property
    def study_end(self):
        if not hasattr(self, '_study_end'):
            self._study_end = self.get_study_end_datetime()
        return self._study_end

    @property
    def study_length(self):
        if self.cohort and self.cohort.study_length:
            return self.cohort.study_length
        else:
            return None

    @property
    def is_active(self):
        return self.active

    @property
    def enabled(self):
        return self.active

    def enable(self):
        if not self.user:
            self.enroll()
        else:
            self.user.is_active = True
            self.user.save()
        self.active = True
        self.save()

    def disable(self):
        if self.user:
            self.user.is_active = False
            self.user.save()
        self.active = False
        self.save()

    @property
    def daily_task_name(self):
        return '%s daily update' % (self.user.username)

    @property
    def daily_task(self):
        try:
            return DailyTask.objects.get(
                user=self.user,
                category=TASK_CATEGORY
            )
        except DailyTask.DoesNotExist:
            return None

    def set_daily_task(self):
        if not hasattr(settings, 'PARTICIPANT_NIGHTLY_UPDATE_TIME'):
            raise ImproperlyConfigured(
                'Participant nightly update time not configured')
        hour, minute = settings.PARTICIPANT_NIGHTLY_UPDATE_TIME.split(':')
        if not self.daily_task:
            self.__create_daily_task()
        self.daily_task.set_time(int(hour), int(minute))

    def __create_daily_task(self):
        task = DailyTask.objects.create(
            user=self.user,
            category=TASK_CATEGORY
        )
        task.create_task(
            task='participants.tasks.daily_update',
            name=self.daily_task_name,
            arguments={
                'username': self.user.username
            }
        )
        return task

    def __str__(self):
        return self.heartsteps_id


class NightlyUpdateRecord(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='+'
    )
    date = models.DateField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    error = models.TextField(
        null=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date'])
        ]


class DataExport(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    filename = models.CharField(max_length=150)
    start = models.DateTimeField()
    end = models.DateTimeField()

    error_message = models.TextField(
        null=True
    )

    def __str__(self):
        return self.filename

    @property
    def export_type(self):
        split_filename = self.filename.split('.')
        if len(split_filename) > 2:
            return split_filename[-2]
        else:
            return 'Unknown'

    @property
    def category(self):
        return self.export_type

    @property
    def duration(self):
        diff = self.end - self.start
        return diff.seconds


class DataExportSummary(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='+'
    )
    category = models.CharField(
        max_length=150
    )

    last_data_export = models.ForeignKey(
        DataExport,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    updated = models.DateTimeField(
        auto_now=True
    )


class DataExportQueue(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='+'
    )

    created = models.DateTimeField(
        auto_now_add=True
    )
    started = models.DateTimeField(
        null=True
    )
    completed = models.DateTimeField(
        null=True
    )
