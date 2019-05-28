import pytz
from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

from daily_tasks.models import DailyTask
from locations.services import LocationService
from participants.signals import nightly_update as participant_nightly_update
from walking_suggestion_times.signals import suggestion_times_updated
from watch_app.signals import step_count_updated

from walking_suggestions.models import SuggestionTime, Configuration
from walking_suggestions.tasks import create_decision, nightly_update

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

class UpdateFromStepCount(TestCase):

    @patch.object(create_decision, 'apply_async')
    def testCreatesDecision(self, create_decision):
        user = User.objects.create(username="test")

        step_count_updated.send(sender=User, username="test")

        create_decision.assert_called_with(kwargs={
            'username': 'test'
        })

class NightlyUpdateTest(TestCase):

    @patch.object(nightly_update, 'apply_async')
    def testQueuesNightlyUpdate(self, nightly_update):
        user = User.objects.create(username="test")

        participant_nightly_update.send(
            sender=User,
            user=user,
            day=date(2019, 5, 7)
        )

        nightly_update.assert_called_with(kwargs={
            'username': 'test',
            'day_string': '2019-05-07'
        })

    