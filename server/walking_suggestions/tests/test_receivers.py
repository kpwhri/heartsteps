import pytz
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth.models import User

from locations.services import LocationService
from locations.signals import timezone_updated
from daily_tasks.models import DailyTask
from walking_suggestion_times.signals import suggestion_times_updated

from walking_suggestions.models import SuggestionTime, Configuration
from walking_suggestions.tasks import initialize_walking_suggestion_service

@override_settings(WALKING_SUGGESTION_TIME_OFFSET=5)
class ConfigutationTest(TestCase):

    def setUp(self):
        timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.addCleanup(timezone_patch.stop)
        self.timezone = timezone_patch.start()
        self.timezone.return_value = pytz.timezone('Etc/GMT+7')

        initialize_walking_suggestion_service_patch = patch.object(initialize_walking_suggestion_service, 'apply_async')
        self.initialize_walking_suggestion_service = initialize_walking_suggestion_service_patch.start()
        self.addCleanup(initialize_walking_suggestion_service_patch.stop)

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

        suggestion_times_updated.send(SuggestionTime, username="test")

        daily_task = DailyTask.objects.get(user=user, category='morning')
        self.assertEqual(daily_task.task.crontab.hour, '15')
        # suggestion minutes should be offset by 5 minutes (see setting override)
        self.assertEqual(daily_task.task.crontab.minute, '10')
        self.initialize_walking_suggestion_service.assert_called()

    def test_creates_configuration_if_does_not_exist(self):
        user = User.objects.create(username="test")

        suggestion_times_updated.send(SuggestionTime, username="test")

        configuration = Configuration.objects.get(user__username="test")
        self.assertEqual(1, Configuration.objects.count())
        self.initialize_walking_suggestion_service.assert_called()

    def test_does_nothing_if_no_user(self):
        suggestion_times_updated.send(SuggestionTime, username="test")        
        self.assertEqual(0, Configuration.objects.count())
        self.initialize_walking_suggestion_service.assert_not_called()
