from unittest.mock import patch
from datetime import datetime, date
import pytz
import uuid

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from activity_logs.models import ActivityLog, ActivityType
from fitbit_api.services import FitbitService

from .models import Day, User, FitbitDay

class ActivitySummaryViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username = "test",
            date_joined = datetime(2018, 9, 9, 9, 9).astimezone(pytz.utc) 
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
        
    def test_fitbit_day_creates_summary(self):
        FitbitDay.objects.create(
            account = self.account,
            date = date(2019, 1 , 6)
        )

        day = Day.objects.get()
        self.assertEqual(day.user.username, self.user.username)
        self.assertEqual(day.date, date(2019, 1, 6))

    def test_fitbit_day_updates_summary(self):
        _day = Day.objects.create(
            user = self.user,
            date = date(2019, 1, 6)
        )

        fitbit_day = FitbitDay.objects.create(
            account = self.account,
            date = date(2019, 1 , 6),
            step_count = 700
        )

        day = Day.objects.get()
        self.assertEqual(day.id, _day.id)
        self.assertEqual(day.steps, fitbit_day.step_count)

        fitbit_day.step_count = 900
        fitbit_day.save()

        day = Day.objects.get()
        self.assertEqual(day.id, _day.id)
        self.assertEqual(day.steps, fitbit_day.step_count)

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