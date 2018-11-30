import pytz
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth.models import User

from locations.services import LocationService
from locations.signals import timezone_updated
from daily_tasks.models import DailyTask

from activity_suggestions.models import SuggestionTime, Configuration

@override_settings(ACTIVITY_SUGGESTION_TIME_OFFSET=5)
class ConfigutationTest(TestCase):

    def setUp(self):
        timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.addCleanup(timezone_patch.stop)
        self.timezone = timezone_patch.start()
        self.timezone.return_value = pytz.timezone('Etc/GMT+7')

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

        daily_task = DailyTask.objects.get(user=user, category='morning')
        self.assertEqual(daily_task.task.crontab.hour, '15')
        # suggestion minutes should be offset by 5 minutes (see setting override)
        self.assertEqual(daily_task.task.crontab.minute, '10')
