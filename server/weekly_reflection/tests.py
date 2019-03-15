from datetime import datetime, date
import json
import pytz
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from daily_tasks.models import DailyTask
from locations.services import LocationService
from push_messages.services import PushMessageService, Device
from weeks.models import Week

from .models import ReflectionTime, User
from .signals import weekly_reflection
from .tasks import send_reflection

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

        timezone_patch = patch.object(timezone, 'now')
        self.now = timezone_patch.start()
        self.now.return_value = datetime(2018, 12, 27, 18).astimezone(pytz.UTC)
        self.addCleanup(timezone_patch.stop)

        location_timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.addCleanup(location_timezone_patch.stop)
        location_timezone = location_timezone_patch.start()
        location_timezone.return_value = pytz.timezone('US/Pacific')

class WeeklyReflectionView(BaseTestCase):

    def test_create_reflection_creates_task(self):
        ReflectionTime.objects.create(
            user = self.user,
            day = 'saturday',
            time = '20:00'
        )

        task = DailyTask.objects.get()
        self.assertTrue(task.enabled)
        self.assertEqual(task.task.task, 'weekly_reflection.tasks.send_reflection')
        self.assertEqual(task.day, 'saturday')
        self.assertEqual(task.hour, 20)
        self.assertEqual(task.minute, 0)

    def test_reflection_time_deactivates_task(self):
        reflection_time = ReflectionTime.objects.create(
            user = self.user,
            day = 'saturday',
            time = '20:00'
        )

        self.assertTrue(reflection_time.daily_task.enabled)

        reflection_time.active = False
        reflection_time.save()

        self.assertFalse(reflection_time.daily_task.enabled)
    
    def test_reflection_time_updates_daily_task(self):
        reflection_time = ReflectionTime.objects.create(
            user = self.user,
            day = 'saturday',
            time = '20:00'
        )

        reflection_time.day = 'sunday'
        reflection_time.time = '8:15'
        reflection_time.save()

        self.assertEqual(reflection_time.daily_task.day, 'sunday')
        self.assertEqual(reflection_time.daily_task.hour, 8)
        self.assertEqual(reflection_time.daily_task.minute, 15)

class WeeklyReflectionTask(TestCase):
    
    @patch.object(weekly_reflection, 'send')
    def test_send_reflection_sends_push_notification(self, weekly_reflection):
        send_reflection('test')

        weekly_reflection.assert_called_with(
            User,
            username = 'test'
        )

class ReflectionTimeView(APITestCase):

    def setUp(self):
        location_timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.addCleanup(location_timezone_patch.stop)
        location_timezone = location_timezone_patch.start()
        location_timezone.return_value = pytz.timezone('US/Pacific')

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
            'day': 'sunday',
            'time': '8:30'
        })

        self.assertEqual(response.status_code, 200)

        reflection_time = ReflectionTime.objects.get(user=user, active=True)
        self.assertEqual(reflection_time.day, 'sunday')
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
            'day': 'saturday',
            'time': '8:30'
        })

        self.assertEqual(response.status_code, 200)

        reflection_time = ReflectionTime.objects.get()
        self.assertEqual(reflection_time.time, '8:30')
        self.assertEqual(reflection_time.day, 'saturday')

    def test_only_accepts_sunday_saturday_reflection_days(self):
        user = User.objects.create(username="test")
        self.client.force_authenticate(user=user)
        
        response = self.client.post(reverse('weekly-reflection-time'), {
            'day': 'saturday',
            'time': '8:30'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('weekly-reflection-time'), {
            'day': 'sunday',
            'time': '8:30'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('weekly-reflection-time'), {
            'day': 'friday',
            'time': '8:30'
        })
        self.assertEqual(response.status_code, 400)
