import pytz
from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

from daily_tasks.models import DailyTask
from locations.services import LocationService
from walking_suggestion_times.signals import suggestion_times_updated
from watch_app.signals import step_count_updated

from walking_suggestions.models import Configuration
from walking_suggestions.models import SuggestionTime
from walking_suggestions.tasks import nightly_update

class ConfigutationTest(TestCase):

    def setUp(self):
        timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.addCleanup(timezone_patch.stop)
        self.timezone = timezone_patch.start()
        self.timezone.return_value = pytz.timezone('Etc/GMT+7')

    def test_creates_configuration_if_does_not_exist(self):
        user = User.objects.create(username="test")

        suggestion_times_updated.send(User, username="test")

        configuration = Configuration.objects.get(user__username="test")
        self.assertEqual(1, Configuration.objects.count())
        self.assertTrue(configuration.enabled)

    def test_does_nothing_if_no_user(self):
        suggestion_times_updated.send(User, username="test")        
        self.assertEqual(0, Configuration.objects.count())
    