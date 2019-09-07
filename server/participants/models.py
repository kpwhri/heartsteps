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
from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from fitbit_api.models import FitbitSubscription
from fitbit_api.models import FitbitSubscriptionUpdate
from page_views.models import PageView
from sms_messages.models import (Contact, Message)
from watch_app.models import StepCount, WatchInstall

TASK_CATEGORY = 'PARTICIPANT_UPDATE'

class Cohort(models.Model):
    name = models.CharField(max_length=75)


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

    @property
    def fitbit_account(self):
        if hasattr(self, '_fitbit_account'):
            return self._fitbit_account
        if not self.user:
            return None
        try:
            account_user = FitbitAccountUser.objects.get(user=self.user)
            self._fitbit_account = account_user.account
            return self._fitbit_account
        except FitbitAccountUser.DoesNotExist:
            return None

    @property
    # A little different from FitbitAccount.authorized
    # FA looks if any of access_token, refresh_token, expires_at are None
    # We now want 3 values for this:
    #   (1) never authorized (no records in FitbitAccount)
    #   (2) currently authorized (valid values in FitbitAccount)
    #   (3) previously authorized (invalid value in extant FitbitAccount record)
    def fitbit_authorized(self):
        if self.fitbit_account:
            if self.fitbit_account.authorized:
                return 'current'
            else:
                return 'prior'
        else:
            return 'never'

    # Changing definitions of first & last updated
    # Had relied on self.fitbit_account.first_updated
    # which in turn depends on FitbitSubscriptionUpdate
    # which isn't behaving as expected
    @property
    def fitbit_first_updated(self):
        if not self._is_enrolled:
            return None
        u = self.user
        if u:
            try:
                min_dt = u.fitbitaccountuser.account.fitbitday_set.filter(
                    wore_fitbit=True).aggregate(mindt=models.Min('date'))
                if min_dt:
                    return min_dt['mindt']
                else:
                    return None
            except (FitbitAccountUser.DoesNotExist,
                    FitbitAccount.DoesNotExist, FitbitDay.DoesNotExist) as e:
                return None
        else:
            return None

    @property
    def fitbit_last_updated(self):
        if not self._is_enrolled:
            return None
        u = self.user
        if u:
            try:
                max_dt = u.fitbitaccountuser.account.fitbitday_set.aggregate(
                         maxdt=models.Max('date'))
                if max_dt:
                    return max_dt['maxdt']
                else:
                    return None
            except (FitbitAccountUser.DoesNotExist,
                    FitbitAccount.DoesNotExist, FitbitDay.DoesNotExist) as e:
                return None
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
                return 0
        else:
            return 0

    @property
    def wore_fitbit_days(self):
        return self._wore_fitbit_days()

    def _watch_app_installed_date(self):
        u = self.user
        if u:
            return u.watchinstall_set.all() \
                  .aggregate(models.Max('created'))['created__max']
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

    def _fitbit_authorized(self):
        return self.fitbit_authorized_date() is not None
    _fitbit_authorized.boolean = True

    # Deprecated.  last_fitbit_sync() no longer exists, always returning 0
    def _last_fitbit_sync_elapsed_hours(self):
        warn("_last_fitbit_sync_elapsed_hours is not expected to work any more")
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
            return u.pageview_set.all() \
                    .aggregate(models.Max('time'))['time__max']
        else:
            return None

    @property
    def last_page_view(self):
        return self._last_page_view

    def _last_watch_app_data(self):
        u = self.user
        if u:
            return u.stepcount_set.all() \
                    .aggregate(models.Max('end'))['end__max']

    @property
    def last_watch_app_data(self):
        return self._last_watch_app_data

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

    def _adherence_no_fitbit_data(self):
        if self._last_fitbit_sync_elapsed_hours() > (24*7):
            return 24*7
        elif self._last_fitbit_sync_elapsed_hours() > (24*3):
            return 72
        elif self._last_fitbit_sync_elapsed_hours() > (24*2):
            return 48
        else:
            return 0

    @property
    def adherence_no_fitbit_data(self):
        return self._adherence_no_fitbit_data

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
            print("Got to user")
            print(u.id)
            participant_number = Contact.objects.get(user=u.id).number
            if participant_number:
                return Message.objects.filter(
                    recipient__exact=participant_number
                    ).values('created', 'body').order_by('-created')
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
