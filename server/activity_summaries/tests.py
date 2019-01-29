from unittest.mock import patch
from datetime import datetime, date
import pytz
import uuid

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from activity_logs.models import ActivityLog, ActivityType
from locations.services import LocationService
from fitbit_api.services import FitbitService
from fitbit_api.models import FitbitDay, FitbitMinuteStepCount

from .models import Day, User

class ActivitySummaryViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username = "test",
            date_joined = datetime(2018, 9, 9, 9, 9).astimezone(pytz.UTC) 
        )
        self.client.force_authenticate(self.user)

    def create_day(self, date):
        Day.objects.create(
            user = self.user,
            date = date,
            moderate_minutes = 10,
            vigorous_minutes = 5,
            total_minutes = 20,
            steps = 10,
            miles = 0.25
        )

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
        response = self.client.get(reverse('activity-summary-date-range', kwargs={
            'start': '2018/10/16',
            'end': 'misformatted date'
        }))

        self.assertEqual(response.status_code, 404)

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

    def make_step_count(self, time):
        FitbitMinuteStepCount.objects.create(
            account = self.account,
            day = self.fitbit_day,
            time = time,
            steps = 300
        )
        
    def test_fitbit_day_creates_summary(self):
        day = Day.objects.get()
        self.assertEqual(day.user.username, self.user.username)
        self.assertEqual(day.date, date(2019, 1, 6))

    def test_fitbit_day_updates_summary(self):
        self.make_step_count(datetime(2019, 1, 6, 8, 30))
        self.make_step_count(datetime(2019, 1, 6, 9, 30))
        self.fitbit_day.save()

        day = Day.objects.get()
        self.assertEqual(day.steps, 600)

        self.make_step_count(datetime(2019, 1, 6, 9, 30))
        self.fitbit_day.save()

        day = Day.objects.get()
        self.assertEqual(day.steps, 900)

class ActivitLogUpdateDay(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="test")

    def create_log_for_date(self, date, vigorous=False):
        activity_type, created = ActivityType.objects.get_or_create(name="run")
        ActivityLog.objects.create(
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
        self.assertEqual(day.moderate_minutes, 10)

    def test_activity_log_updates_day(self):
        self.create_log_for_date(date(2019, 1, 6))

        day = Day.objects.get()
        self.assertEqual(day.user.username, self.user.username)
        self.assertEqual(day.moderate_minutes, 10)

        self.create_log_for_date(date(2019, 1, 6))

        day = Day.objects.get()
        self.assertEqual(day.user.username, self.user.username)
        self.assertEqual(day.moderate_minutes, 20)

        self.create_log_for_date(date(2019, 1, 6), True)
        
        day = Day.objects.get()
        self.assertEqual(day.user.username, self.user.username)
        self.assertEqual(day.moderate_minutes, 20)
        self.assertEqual(day.vigorous_minutes, 10)
        self.assertEqual(day.total_minutes, 40)
