from datetime import datetime, date
import json
import pytz
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from locations.services import LocationService
from weeks.models import Week

from .models import ReflectionTime, User

class ReflectionTimeUpdatesWeek(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

        timezone_patch = patch.object(timezone, 'now')
        self.now = timezone_patch.start()
        self.now.return_value = datetime(2018, 12, 27, 18)
        self.addCleanup(timezone_patch.stop)

        location_timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.addCleanup(location_timezone_patch.stop)
        location_timezone = location_timezone_patch.start()
        location_timezone.return_value = pytz.timezone('US/Pacific')

    def test_creates_week_if_none_exists(self):

        ReflectionTime.objects.create(
            user = self.user,
            day = 'sunday',
            time = '8:30'
        )

        week = Week.objects.get(user=self.user)
        self.assertEqual(week.start_date, date(2018, 12, 24))
        self.assertEqual(week.end_date, date(2018, 12, 30))

    def test_updates_week_end_date(self):
        Week.objects.create(
            user = self.user,
            start_date = date(2018, 12, 24),
            end_date = date(2018, 12, 30)
        )

        ReflectionTime.objects.create(
            user = self.user,
            day = 'saturday',
            time = '17:00'
        )

        week = Week.objects.get(user=self.user)
        self.assertEqual(week.start_date, date(2018, 12, 24))
        self.assertEqual(week.end_date, date(2018, 12, 29))
        

class ReflectionTimeView(APITestCase):

    def test_returns_reflection_time(self):
        user = User.objects.create(username="test")

        ReflectionTime.objects.create(
            user = user,
            day = 'sunday',
            time = '19:00'
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('weekly-reflection-time'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['day'], 'sunday')
        self.assertEqual(response.data['time'], '19:00')

    def test_returns_404_if_no_reflection_time(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('weekly-reflection-time'))

        self.assertEqual(response.status_code, 404)

    def test_create_reflection_time(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('weekly-reflection-time'), {
            'day': 'monday',
            'time': '8:30'
        })

        self.assertEqual(response.status_code, 200)

        reflection_time = ReflectionTime.objects.get(user=user, active=True)
        self.assertEqual(reflection_time.day, 'monday')
        self.assertEqual(reflection_time.time, '8:30')

    def test_updates_reflection_time(self):
        user = User.objects.create(username="test")
        ReflectionTime.objects.create(
            user = user,
            day = 'sunday',
            time = '19:00'
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('weekly-reflection-time'), {
            'day': 'monday',
            'time': '8:30'
        })

        self.assertEqual(response.status_code, 200)

        self.assertEqual(ReflectionTime.objects.filter(user=user).count(), 2)
        self.assertEqual(ReflectionTime.objects.filter(user=user, active=True).count(), 1)        