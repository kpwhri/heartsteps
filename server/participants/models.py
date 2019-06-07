import json
import pytz
from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from daily_tasks.models import DailyTask
from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser

TASK_CATEGORY = 'PARTICIPANT_UPDATE'


class Participant(models.Model):
    """
    Represents a study participant

    When the participant is enrolled, a user is created.
    """
    heartsteps_id = models.CharField(primary_key=True, unique=True, max_length=25)
    enrollment_token = models.CharField(max_length=10, unique=True)
    birth_year = models.CharField(max_length=4, null=True, blank=True)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    class NotEnrolled(RuntimeError):
        pass

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

    def _wore_fitbit_days(self):
        if not self._is_enrolled:
            return 0

        u = self.user
        if u:
            try:
                return u.fitbitaccountuser.account.fitbitday_set.filter(
                    wore_fitbit=True).count()
            except (FitbitAccountUser.DoesNotExist,
                     FitbitAccount.DoesNotExist, FitbitDay.DoesNotExist) as e:
                print("Error in " + u.username + ": " + str(e))
                return 0
        else:
            return 0

    @property
    def wore_fitbit_days(self):
        return self._wore_fitbit_days()

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
