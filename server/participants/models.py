import json
import logging
import pytz
from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from daily_tasks.models import DailyTask
from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser, \
    FitbitSubscription, FitbitSubscriptionUpdate
from page_views.models import PageView
from watch_app.models import StepCount, WatchInstall

TASK_CATEGORY = 'PARTICIPANT_UPDATE'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def _enrollment_date(self):
        if self.user:
            return self.user.date_joined
        else:
            return None

    @property
    def enrollment_date(self):
        return self._enrollment_date

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
                logger.info("_wore_fitbit_days Error in " + u.username + ": " + str(e))
                return 0
        else:
            return 0

    @property
    def wore_fitbit_days(self):
        return self._wore_fitbit_days()

    def _watch_app_installed_date(self):
        u = self.user
        if u:
            dt = u.watchinstall_set.all() \
                  .aggregate(models.Max('created'))['created__max']
            return dt
        else:
            return None

    @property
    def watch_app_installed_date(self):
        return self._watch_app_installed_date

    def _watch_app_installed(self):
        return self._watch_app_installed_date() is not None
    _watch_app_installed.boolean = True

    @property
    def watch_app_installed(self):
        return self._watch_app_installed

    def _fitbit_authorized_date(self):
        u = self.user
        if u:
            dt = u.authenticationsession_set.all() \
                  .aggregate(models.Max('created'))['created__max']
            return dt
        else:
            return False

    @property
    def fitbit_authorized_date(self):
        return self._fitbit_authorized_date

    def _fitbit_authorized(self):
        return self.fitbit_authorized_date() is not None
    _fitbit_authorized.boolean = True

    @property
    def fitbit_authorized(self):
        return self._fitbit_authorized()

    def _last_fitbit_sync(self):
        if not self._is_enrolled:
            return 0

        u = self.user
        if u:
            try:
                return u.fitbitaccountuser.account \
                    .fitbitsubscription_set.get() \
                    .fitbitsubscriptionupdate_set.all() \
                    .aggregate(models.Max('created'))['created__max']
            except (FitbitAccountUser.DoesNotExist, FitbitAccount.DoesNotExist,
                    FitbitSubscription.DoesNotExist,
                    FitbitSubscriptionUpdate.DoesNotExist) as e:
                logger.info("_last_fitbit_sync Error in " + u.username + ": " + str(e))
                return 0
        else:
            return 0

    @property
    def last_fitbit_sync(self):
        return self._last_fitbit_sync

    def _last_fitbit_sync_elapsed_hours(self):
        if self._last_fitbit_sync() == 0 or self.last_fitbit_sync() is None:
            return 0
        else:
            elapsed = pytz.utc.localize(datetime.now()) - self._last_fitbit_sync()
            return elapsed.total_seconds() // 3600

    def _last_page_view(self):
        if not self._is_enrolled:
            return None

        u = self.user
        if u:
            r = u.pageview_set.all() \
                    .aggregate(models.Max('time'))['time__max']
            return r
        else:
            return None

    @property
    def last_page_view(self):
        return self._last_page_view

    def _adherence_install_app(self):
        if self._last_page_view() is None:
            if self._wore_fitbit_days() >= 7:
                return True
            else:
                return False
        else:
            return False
    _adherence_install_app.boolean = True

    @property
    def adherence_install_app(self):
        return self._adherence_install_app

    @property
    def adherence_no_fitbit_data(self):
        if self._last_fitbit_sync_elapsed_hours() > (24*7):
            return 24*7
        elif self._last_fitbit_sync_elapsed_hours() > (24*3):
            return 72
        elif self._last_fitbit_sync_elapsed_hours() > (24*2):
            return 48
        else:
            return 0

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
