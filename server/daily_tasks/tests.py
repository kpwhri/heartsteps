import pytz
from unittest.mock import patch

from django.test import TestCase, override_settings

from django_celery_beat.models import PeriodicTask, PeriodicTasks

from locations.services import LocationService
from locations.signals import timezone_updated

from .models import User, DailyTask

class DailyTaskUpdateTest(TestCase):

    def setUp(self):
        timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.addCleanup(timezone_patch.stop)
        self.timezone = timezone_patch.start()
        self.timezone.return_value = pytz.timezone('Etc/GMT+7')

    def create_task(self, minute=0, hour=0, day=None):
        return DailyTask.create_daily_task(
            user = User.objects.create(username="test"),
            category = 'example',
            task = 'example.example.task',
            name = 'Name of task!',
            arguments = {},
            day = day,
            hour = hour,
            minute = minute
        )

    def test_updates_tasks_with_timezone(self):
        self.create_task(
            minute = 0,
            hour = 2
        )

        task = PeriodicTask.objects.get()
        # hour was set to 2, timezone is +7 == 9 GMT
        self.assertEqual(task.crontab.hour, '9')
        self.assertEqual(task.crontab.minute, '0')

        self.timezone.return_value = pytz.timezone('Etc/GMT+4')
        timezone_updated.send(User, username="test")

        task = PeriodicTask.objects.get()
        # hour was set to 2, timezone is +4
        self.assertEqual(task.crontab.hour, '6')
        self.assertEqual(task.crontab.minute, '0')

    def test_registers_tasks_for_specific_day(self):
        self.timezone.return_value = pytz.timezone('Etc/GMT-8')
        self.create_task(
            minute = 30,
            hour = 20,
            day = 'friday'
        )

        task = PeriodicTask.objects.get()
        self.assertEqual(task.crontab.day_of_week, '5')

    def test_regiesters_correct_day_with_timezone_change(self):
        self.timezone.return_value = pytz.timezone('UTC')
        self.create_task(
            hour = 6,
            day = 'sunday'
        )

        task = PeriodicTask.objects.get()
        self.assertEqual(task.crontab.day_of_week, '0')
        self.assertEqual(task.crontab.hour, '6')

        self.timezone.return_value = pytz.timezone('Etc/GMT-8')
        timezone_updated.send(User, username="test")

        task = PeriodicTask.objects.get()
        self.assertEqual(task.crontab.day_of_week, '6')
        self.assertEqual(task.crontab.hour, '22')
