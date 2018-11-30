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

    def test_updates_tasks_with_timezone(self):
        DailyTask.create_daily_task(
            user = User.objects.create(username="test"),
            category = 'example',
            task = 'example.example.task',
            name = 'Name of task!',
            arguments = {},
            hour = 2,
            minute = 0
        )

        task = PeriodicTask.objects.get()
        # hour was set to 2, timezone is +7 == 9 GMT
        self.assertEqual(task.crontab.hour, '9')

        self.timezone.return_value = pytz.timezone('Etc/GMT+4')
        timezone_updated.send(User, username="test")

        task = PeriodicTask.objects.get()
        # hour was set to 2, timezone is +4
        self.assertEqual(task.crontab.hour, '6')
