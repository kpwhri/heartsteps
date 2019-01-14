import pytz
from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from fitbit_api.models import FitbitAccount, FitbitAccountUser, FitbitActivityType, FitbitDay, FitbitActivity
from activity_logs.models import ActivityType, ActivityLog, User

from .models import FitbitActivityToActivityType

class FitbitActivityLogTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.account = FitbitAccount.objects.create(fitbit_user="test")
        FitbitAccountUser.objects.create(
            user = self.user,
            account = self.account
        )

    def create_fitbit_activity(self, fitbit_activity_type=None):
        now = timezone.now()
        fitbit_day, _ = FitbitDay.objects.get_or_create(
            account = self.account,
            date = datetime(now.year, now.month, now.day).astimezone(pytz.UTC)
        )
        if not fitbit_activity_type:
            fitbit_activity_type, _ = FitbitActivityType.objects.get_or_create(fitbit_id="234", name="foobar")
        return FitbitActivity.objects.create(
            account = self.account,
            type = fitbit_activity_type,
            day = fitbit_day,
            start_time = now - timedelta(minutes=20),
            end_time = now,
            average_heart_rate = 70
        )

    def test_fitbit_activity_types_linked_to_activity_type(self):
        self.create_fitbit_activity()

        activity_type = ActivityType.objects.get()
        self.assertEqual(activity_type.name, 'foobar')
        self.assertEqual(FitbitActivityToActivityType.objects.count(), 1)

        new_fitbit_activity_type = FitbitActivityType.objects.create(fitbit_id="567", name="foobar")
        self.create_fitbit_activity(new_fitbit_activity_type)

        activity_type = ActivityType.objects.get()
        self.assertEqual(activity_type.name, 'foobar')
        self.assertEqual(FitbitActivityToActivityType.objects.count(), 2)

    def test_fitbit_activity_creates_activity_log(self):
        self.create_fitbit_activity()

        activity_log = ActivityLog.objects.get()
        self.assertEqual(activity_log.user, self.user)
        self.assertEqual(activity_log.type.name, 'foobar')
        self.assertEqual(activity_log.duration, 20)

    def test_fitbit_activity_updates_activity_log(self):
        fitbit_activity = self.create_fitbit_activity()

        activity_log = ActivityLog.objects.get()
        self.assertEqual(activity_log.duration, 20)

        fitbit_activity.end_time = timezone.now() + timedelta(minutes=10)
        fitbit_activity.save()

        activity_log = ActivityLog.objects.get()
        self.assertEqual(activity_log.duration, 30)

    def test_will_not_update_activity_log_if_changed(self):
        fitbit_activity = self.create_fitbit_activity()

        activity_log = ActivityLog.objects.get()
        self.assertEqual(activity_log.duration, 20)
        
        activity_log.vigorous = True
        activity_log.save()
        fitbit_activity.end_time = timezone.now() + timedelta(minutes=10)
        fitbit_activity.save()

        activity_log = ActivityLog.objects.get()
        self.assertEqual(activity_log.duration, 20)
        