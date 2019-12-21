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
    heartsteps_id = models.CharField(primary_key=True, unique=True, max_length=25)
    enrollment_token = models.CharField(max_length=10, unique=True)
    birth_year = models.CharField(max_length=4, null=True, blank=True)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    cohort = models.ForeignKey(
        Cohort,
        null = True,
        on_delete = models.SET_NULL
    )

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

    def _is_enrolled(self):
        if self.user:
            return True
        else:
            return False
    _is_enrolled.boolean = True

    @property
    def enrollment_date(self):
        return self.date_joined

    @property
    def date_joined(self):
        if self.user:
            return self.user.date_joined
        else:
            return None

    def _is_active(self):
        try:
            daily_task = self.__get_daily_task()
            if daily_task.enabled:
                return True
        except DailyTask.DoesNotExist:
            pass
        return False
    _is_active.boolean = True

    @property
    def is_active(self):
        return self._is_active

    @property
    def enrolled(self):
        return self._is_enrolled()

    def _last_page_view(self):
        if not self._is_enrolled:
            return None

        u = self.user
        if u:
            return u.pageview_set.all() \
                    .aggregate(models.Max('time'))['time__max']
        else:
            return None

    @property
    def last_page_view(self):
        return self._last_page_view

    def _adherence_app_use(self):
        if self._last_page_view() is None:
            return 0
        else:
            elapsed = pytz.utc.localize(datetime.now()) - self._last_page_view()
            elapsed_hours = elapsed.total_seconds() // 3600
            if elapsed_hours > (24*7):
                return 24*7
            elif elapsed_hours > 96:
                return 96
            else:
                return 0

    @property
    def adherence_app_use(self):
        return self._adherence_app_use

    def _last_text_sent(self):
        u = self.user
        if u:
            participant_number = Contact.objects.get(user=u.id).number
            last_text_sent = Message.objects.filter(
                recipient__exact=participant_number).latest('created').created
            return last_text_sent
        else:
            return None

    @property
    def last_text_sent(self):
        return self._last_text_sent

    def _text_message_history(self):
        u = self.user
        if u:
            participant_number = Contact.objects.get(user=u.id).number
            if participant_number:
                return Message.objects.filter(
                    recipient__exact=participant_number
                    ).only('created', 'body').order_by('-created')
            else:
                return None
        else:
            return None

    @property
    def text_message_history(self):
        return self._text_message_history

    @property
    def date_enrolled(self):
        if self.user:
            day_service = DayService(user=self.user)
            return day_service.get_date_at(self.user.date_joined)
        else:
            raise self.NotEnrolled('Not enrolled')

    @property
    def daily_task_name(self):
        return '%s daily update' % (self.user.username)

    @property
    def daily_task(self):
        try:
            return self.__get_daily_task()
        except DailyTask.DoesNotExist:
            return None

    def set_daily_task(self):
        if not hasattr(settings, 'PARTICIPANT_NIGHTLY_UPDATE_TIME'):
            raise ImproperlyConfigured('Participant nightly update time not configured')
        hour, minute = settings.PARTICIPANT_NIGHTLY_UPDATE_TIME.split(':')
        try:
            daily_task = self.__get_daily_task()
        except DailyTask.DoesNotExist:
            daily_task = self.__create_daily_task()
        daily_task.set_time(int(hour), int(minute))

    def __get_daily_task(self):
        return DailyTask.objects.get(
            user = self.user,
            category = TASK_CATEGORY
        )

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
