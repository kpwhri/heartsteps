from unittest.mock import patch

from django.test import TestCase, override_settings

from daily_tasks.models import DailyTask
from morning_messages.models import Configuration as MorningMessageConfiguration
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration

from participants.models import Participant, User, TASK_CATEGORY
from participants.tasks import initialize_participant

@override_settings(PARTICIPANT_NIGHTLY_UPDATE_TIME='4:15')
class InitializeTask(TestCase):

    def setUp(self):
        Participant.objects.create(
            user = User.objects.create(username="test")
        )

    def test_starts_nightly_update_task(self):
        initialize_participant("test")

        daily_task = DailyTask.objects.get(user__username="test", category=TASK_CATEGORY)
        self.assertEqual(daily_task.hour, 4)
        self.assertEqual(daily_task.minute, 15)
    
    def test_creates_walking_suggestion_configuration(self):
        initialize_participant("test")

        configuration = WalkingSuggestionConfiguration.objects.get(user__username="test")
        self.assertIsNotNone(configuration)

    def test_creates_morning_message_configuration(self):
        initialize_participant("test")

        configuration = MorningMessageConfiguration.objects.get()
        self.assertEqual(configuration.user.username, "test")
