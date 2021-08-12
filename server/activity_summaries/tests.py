from unittest.mock import patch
from datetime import datetime, date, timedelta
import pytz
import uuid

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from activity_logs.models import ActivityLog, ActivityType
from locations.services import LocationService
from fitbit_api.services import FitbitService, FitbitClient
from fitbit_activities.services import FitbitDayService
from fitbit_activities.models import FitbitDay, FitbitMinuteStepCount


from .models import ActivitySummary
from .models import Day
from .models import User

class TestBase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username = "test",
            date_joined = datetime(2018, 9, 9, 9, 9).astimezone(pytz.UTC) 
        )
        self.client.force_authenticate(self.user)

    def create_day(self, date):
        return Day.objects.create(
            user = self.user,
            date = date,
            moderate_minutes = 10,
            vigorous_minutes = 5,
            total_minutes = 20,
            steps = 10,
            miles = 0.25
        )

class ActivitySummaryViewTests(TestBase):

    def setUp(self):
        self.user = User.objects.create(
            username = "test",
            date_joined = datetime(2018, 9, 9, 9, 9).astimezone(pytz.UTC) 
        )
        self.client.force_authenticate(self.user)

    def test_get_invalid_date(self):
        response = self.client.get(reverse('activity-summary-day', kwargs={
            'day': '2018-9-6'
        }))

        self.assertEqual(response.status_code, 404)

    def test_get_default_date(self):
        response = self.client.get(reverse('activity-summary-day', kwargs={
            'day': '2018-12-10'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['steps'], 0)
        self.assertEqual(response.data['miles'], 0)
        self.assertEqual(response.data['minutes'], 0)
        self.assertEqual(response.data['moderateMinutes'], 0)
        self.assertEqual(response.data['vigorousMinutes'], 0)
        self.assertIsNotNone(response.data['updated'])

    def test_get_day(self):
        self.create_day(date(2018, 10, 16))

        response = self.client.get(reverse('activity-summary-day', kwargs={
            'day': '2018-10-16'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['date'], '2018-10-16')
        self.assertEqual(response.data['steps'], 10)
        self.assertEqual(response.data['miles'], 0.25)
        self.assertEqual(response.data['moderateMinutes'], 10)
        self.assertEqual(response.data['vigorousMinutes'], 5)
        self.assertEqual(response.data['minutes'], 20)


    def test_get_date_range(self):
        self.create_day(datetime(2018, 10, 16))
        self.create_day(datetime(2018, 10, 17))
        self.create_day(datetime(2018, 10, 18))
        self.create_day(datetime(2018, 10, 19))

        response = self.client.get(reverse('activity-summary-date-range', kwargs={
            'start': '2018-10-16',
            'end': '2018-10-18'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[-1]['date'], '2018-10-18')

    def test_get_date_range_creates_days(self):
        self.assertEqual(Day.objects.count(), 0)

        response = self.client.get(reverse('activity-summary-date-range', kwargs={
            'start': '2018-10-16',
            'end': '2018-10-18'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(Day.objects.count(), 3)

        response = self.client.get(reverse('activity-summary-date-range', kwargs={
            'start': '2018-10-17',
            'end': '2018-10-19'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Day.objects.count(), 4)

    def test_date_range_misformatted(self):
        self.assertRaises(ValueError, self.client.get, reverse('activity-summary-date-range', kwargs={
            'start': '2018/10/16',
            'end': 'misformatted date'
        }))

    @patch.object(FitbitClient, 'get_timezone', return_value=pytz.UTC)
    @patch.object(FitbitDayService, 'update')
    def test_updates_day(self, fitbit_day_update, get_timezone):
        FitbitService.create_account(
            user = self.user
        )

        response = self.client.get(reverse('activity-summary-day-update', kwargs={
            'day': '2018-12-10'
        }))

        fitbit_day_update.assert_called()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['steps'], 0)
        self.assertEqual(response.data['miles'], 0)
        self.assertEqual(response.data['minutes'], 0)
        self.assertEqual(response.data['moderateMinutes'], 0)
        self.assertEqual(response.data['vigorousMinutes'], 0)

    @patch.object(FitbitDayService, 'update')
    def test_update_day_fails(self, fitbit_day_update):
        response = self.client.get(reverse('activity-summary-day-update', kwargs={
            'day': '2018-12-10'
        }))

        fitbit_day_update.assert_not_called()

        self.assertEqual(response.status_code, 400)

    def test_get_activity_summary(self):
        today = self.create_day(date.today())

        response = self.client.get(reverse('activity-summary'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['activities_completed'], today.activities_completed)
        self.assertEqual(response.data['miles'], today.miles)
        self.assertEqual(response.data['steps'], today.steps)
        self.assertEqual(response.data['minutes'], today.total_minutes)
        assert 'updated' in response.data

class FitbitDayUpdatesDay(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.account = FitbitService.create_account(
            user = self.user
        )
        self.fitbit_day = FitbitDay.objects.create(
            account = self.account,
            date = date(2019, 1, 6)
        )
        
    def test_fitbit_day_creates_summary(self):
        day = Day.objects.get()
        self.assertEqual(day.user.username, self.user.username)
        self.assertEqual(day.date, date(2019, 1, 6))

    def test_fitbit_day_updates_summary(self):
        self.fitbit_day.step_count = 600
        self.fitbit_day.distance = 1.234
        self.fitbit_day.save()

        day = Day.objects.get()
        self.assertEqual(day.steps, 600)
        self.assertEqual(day.miles, 1.234)

        self.fitbit_day.step_count = 900
        self.fitbit_day.save()

        day = Day.objects.get()
        self.assertEqual(day.steps, 900)

    def test_updating_fitbit_with_multiple_day_summaries(self):
        """
        This test is a quick fix for issue #122 on github
        https://github.com/kpwhri/heartsteps/issues/122

        We want to make sure having multiple day entries, which is a bug
        don't cause updating fitbit information to break.
        Note: We don't know why multiple day entries are being created.
        """
        Day.objects.create(
            user = self.user,
            date = date(2019, 1 ,6)
        )
        Day.objects.create(
            user = self.user,
            date = date(2019, 1 ,6)
        )

        self.fitbit_day.step_count = 600
        self.fitbit_day.distance = 1.234
        self.fitbit_day.save()

        days = Day.objects.filter(
            user=self.user,
            date=date(2019,1,6)
        ) \
        .all()
        for day in days:
            self.assertEqual(day.steps, 600)
        self.assertEqual(len(days), 3)

class ActivitLogUpdateDay(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            date_joined = datetime(2019, 1, 5).astimezone(pytz.UTC)
        )

    def create_log_for_date(self, date, vigorous=False):
        activity_type, created = ActivityType.objects.get_or_create(name="run")
        return ActivityLog.objects.create(
            user = self.user,
            type = activity_type,
            start = timezone.now().replace(
                year = date.year,
                month = date.month,
                day = date.day
            ),
            duration = 10,
            vigorous = vigorous
        )

    def test_activity_log_creates_day(self):
        self.create_log_for_date(date(2019, 1, 6))

        day = Day.objects.get()
        self.assertEqual(day.user.username, self.user.username)
        self.assertEqual(day.activities_completed, 1)
        self.assertEqual(day.moderate_minutes, 10)

    def test_activity_log_updates_day(self):
        self.create_log_for_date(date(2019, 1, 6))

        day = Day.objects.get()
        self.assertEqual(day.activities_completed, 1)
        self.assertEqual(day.moderate_minutes, 10)

        self.create_log_for_date(date(2019, 1, 6))

        day = Day.objects.get()
        self.assertEqual(day.activities_completed, 2)
        self.assertEqual(day.moderate_minutes, 20)

        activity_log = self.create_log_for_date(date(2019, 1, 6), True)
        
        day = Day.objects.get()
        self.assertEqual(day.activities_completed, 3)
        self.assertEqual(day.moderate_minutes, 20)
        self.assertEqual(day.vigorous_minutes, 10)
        self.assertEqual(day.total_minutes, 40)

        activity_log.delete()

        day = Day.objects.get()
        self.assertEqual(day.activities_completed, 2)
        self.assertEqual(day.total_minutes, 20)

    def test_updates_multiple_activity_summaries_if_exists(self):
        """
        This test is a quick fix for issue #122 on github
        https://github.com/kpwhri/heartsteps/issues/122

        We want to make sure having multiple day entries, which is a bug
        don't cause updating fitbit information to break.
        Note: We don't know why multiple day entries are being created.
        """
        Day.objects.create(
            user = self.user,
            date = date(2019, 1 ,6)
        )
        Day.objects.create(
            user = self.user,
            date = date(2019, 1 ,6)
        )

        self.create_log_for_date(date(2019, 1, 6))

        days = Day.objects.filter(
            user=self.user,
            date=date(2019,1,6)
        ) \
        .all()
        for day in days:
            self.assertEqual(day.activities_completed, 1)
            self.assertEqual(day.moderate_minutes, 10)
        self.assertEqual(len(days), 2)

class ActivitSummary(TestBase):
    
    def test_activity_summary_updated_after_day_summary_saved(self):
        
        day = self.create_day(date.today())

        summary = ActivitySummary.objects.get(user = self.user)
        self.assertEqual(summary.activities_completed, day.activities_completed)
        self.assertEqual(summary.miles, day.miles)
        self.assertEqual(summary.minutes, day.total_minutes)
        self.assertEqual(summary.steps, day.steps)

        day.miles = 3
        day.steps = 1000
        day.save()

        summary = ActivitySummary.objects.get(user = self.user)
        self.assertEqual(summary.miles, day.miles)
        self.assertEqual(summary.steps, day.steps)

    def test_activity_summary_updates_for_multiple_days(self):
        yesterday = self.create_day(date.today() - timedelta(days=1))

        summary = ActivitySummary.objects.get(user = self.user)
        self.assertEqual(summary.activities_completed, yesterday.activities_completed)
        self.assertEqual(summary.miles, yesterday.miles)
        self.assertEqual(summary.minutes, yesterday.total_minutes)
        self.assertEqual(summary.steps, yesterday.steps)

        today = self.create_day(date.today())

        summary = ActivitySummary.objects.get(user = self.user)
        self.assertEqual(summary.activities_completed, today.activities_completed + yesterday.activities_completed)
        self.assertEqual(summary.miles, today.miles + yesterday.miles)
        self.assertEqual(summary.minutes, today.total_minutes + yesterday.total_minutes)
        self.assertEqual(summary.steps, today.steps + yesterday.steps)

        today.delete()

        summary = ActivitySummary.objects.get(user = self.user)
        self.assertEqual(summary.activities_completed, yesterday.activities_completed)
        self.assertEqual(summary.miles, yesterday.miles)
        self.assertEqual(summary.minutes, yesterday.total_minutes)
        self.assertEqual(summary.steps, yesterday.steps)

    def test_activity_summary_handles_multiple_days_for_single_date(self):
        yesterday = self.create_day(date.today() - timedelta(days=1))
        today = self.create_day(date.today())
        second_today = self.create_day(date.today())

        summary = ActivitySummary.objects.get(user = self.user)
        self.assertEqual(summary.activities_completed, today.activities_completed + yesterday.activities_completed)
        self.assertEqual(summary.miles, today.miles + yesterday.miles)
        self.assertEqual(summary.minutes, today.total_minutes + yesterday.total_minutes)
        self.assertEqual(summary.steps, today.steps + yesterday.steps)
