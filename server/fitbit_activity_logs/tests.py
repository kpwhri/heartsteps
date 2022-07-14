from unittest.mock import patch
import pytz
from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from fitbit_api.models import FitbitAccount, FitbitAccountUser
from fitbit_activities.models import FitbitActivityType, FitbitDay, FitbitActivity
from activity_logs.models import ActivityType, ActivityLog, User
from participants.models import Participant
from fitbit_api.models import FitbitConsumerKey

from .models import FitbitActivityToActivityType

class FitbitActivityLogTests(TestCase):

    def setUp(self):
        FitbitConsumerKey.objects.create(key='key', secret='secret')
        self.user = User.objects.create(username="test")
        self.participant = Participant.objects.create(
            user = self.user,
            heartsteps_id = "test",
            enrollment_token = "test",
            birth_year = 1990
        )
        self.account = FitbitAccount.objects.create(fitbit_user="test")
        FitbitAccountUser.create_or_update(
            user = self.user,
            account = self.account
        )

    def create_fitbit_activity(self, fitbit_activity_type=None, average_heart_rate=70, duration=20):
        now = timezone.now()
        fitbit_day, _ = FitbitDay.objects.get_or_create(
            account = self.account,
            date = datetime(now.year, now.month, now.day).astimezone(pytz.UTC)
        )
        if not fitbit_activity_type:
            fitbit_activity_type, _ = FitbitActivityType.objects.get_or_create(fitbit_id="234", account=self.account, name="Foobar")
        return FitbitActivity.objects.create(
            account = self.account,
            type = fitbit_activity_type,
            start_time = now - timedelta(minutes=duration),
            end_time = now,
            average_heart_rate = average_heart_rate
        )

    def test_fitbit_activity_types_linked_to_activity_type(self):
        fitbit_activity_type = FitbitActivityType.objects.create(
            fitbit_id = "1234",
            account= self.account,
            name = "Foobar"
        )

        activity_type = ActivityType.objects.get()
        self.assertEqual(activity_type.name, 'foobar')
        self.assertEqual(activity_type.title, 'Foobar')
        connector = FitbitActivityToActivityType.objects.get()
        self.assertEqual(connector.activity_type, activity_type)
        self.assertEqual(connector.fitbit_activity_type.id, fitbit_activity_type.id)
    
    def test_similar_fitbit_activity_types_grouped_together(self):
        FitbitActivityType.objects.create(fitbit_id="567", account=self.account, name="FooBar")
        FitbitActivityType.objects.create(fitbit_id="577", account=self.account, name="Foobar")

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

        fitbit_activity.end_time = fitbit_activity.end_time + timedelta(minutes=10)
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
    
    @patch.object(timezone, 'now', return_value=datetime(2020, 1, 1, 0, 0, tzinfo=pytz.UTC))
    def test_marks_activity_as_vigorous(self, timezone):
        self.participant.birth_year = 1970
        self.participant.save()

        fitbit_activity = self.create_fitbit_activity(average_heart_rate = 120)

        activity_log = ActivityLog.objects.get()
        self.assertTrue(activity_log.vigorous)

    @patch.object(timezone, 'now', return_value=datetime(2020, 1, 1, 0, 0, tzinfo=pytz.UTC))
    def test_marks_activity_not_vigorous(self, timezone):
        self.participant.birth_year = 1970
        self.participant.save()

        fitbit_activity = self.create_fitbit_activity(average_heart_rate = 110)

        activity_log = ActivityLog.objects.get()
        self.assertFalse(activity_log.vigorous)

    def test_no_activity_log_if_duration_less_than_10(self):
        fitbit_activity = self.create_fitbit_activity(duration=9)
        
        self.assertEqual(ActivityLog.objects.count(), 0)
        