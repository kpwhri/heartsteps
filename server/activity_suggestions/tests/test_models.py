import pytz
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth.models import User

from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule

from locations.services import LocationService
from locations.signals import timezone_updated

from activity_suggestions.models import SuggestionTime, Configuration, DailyTask

@override_settings(ACTIVITY_SUGGESTION_TIME_OFFSET=5)
@override_settings(ACTIVITY_SUGGESTION_UPDATE_TIME='2:00')
class ConfigutationTest(TestCase):

    def setUp(self):
        timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.addCleanup(timezone_patch.stop)
        self.timezone = timezone_patch.start()
        self.timezone.return_value = pytz.timezone('Etc/GMT+7')

    @patch.object(PeriodicTasks, 'changed')
    def test_creates_nightly_task(self, periodic_tasks_changed):
        Configuration.objects.create(
            user = User.objects.create(username="test")
        )

        task = PeriodicTask.objects.get()
        self.assertEqual(task.name, 'Activity suggestion nightly update for test')
        # midnight local time, shown at UTC timezone
        self.assertEqual(task.crontab.hour, '9')
        self.assertEqual(task.crontab.minute, '0')
        periodic_tasks_changed.assert_called()

    def test_updates_tasks_with_timezone(self):
        configuration = Configuration.objects.create(
            user = User.objects.create(username="test")
        )

        task = PeriodicTask.objects.get()
        self.assertEqual(task.crontab.hour, '9')

        self.timezone.return_value = pytz.timezone('Etc/GMT+4')
        timezone_updated.send(User, username="test")

        task = PeriodicTask.objects.get()
        self.assertEqual(task.crontab.hour, '6')

    def test_creates_tasks_for_suggestion_times(self):
        user = User.objects.create(username="test")
        SuggestionTime.objects.create(
            user = user,
            category = 'morning',
            hour = 8,
            minute = 15
        )
        configuration = Configuration.objects.create(
            user = user
        )

        daily_task = DailyTask.objects.get(configuration=configuration, category='morning')
        self.assertEqual(daily_task.task.crontab.hour, '15')
        self.assertEqual(daily_task.task.crontab.minute, '10')
