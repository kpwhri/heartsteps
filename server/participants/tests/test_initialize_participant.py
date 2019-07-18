from unittest.mock import patch

from django.test import TestCase, override_settings

from daily_tasks.models import DailyTask
from anti_sedentary.models import Configuration as AntiSedentaryConfiguration
from morning_messages.models import Configuration as MorningMessageConfiguration
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration

from participants.models import Participant, User, TASK_CATEGORY
from participants.services import ParticipantService
from participants.signals import initialize_participant

@override_settings(PARTICIPANT_NIGHTLY_UPDATE_TIME='4:15')
class InitializeTask(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.participant = Participant.objects.create(
            heartsteps_id = 'test',
            user = self.user
        )

    def test_starts_nightly_update_task(self):
        service = ParticipantService(username="test")
        service.initialize()

        daily_task = DailyTask.objects.get(user__username="test", category=TASK_CATEGORY)
        self.assertEqual(daily_task.hour, 4)
        self.assertEqual(daily_task.minute, 15)
    
    def test_creates_walking_suggestion_configuration(self):
        service = ParticipantService(username="test")
        service.initialize()

        configuration = WalkingSuggestionConfiguration.objects.get(user__username="test")
        self.assertIsNotNone(configuration)

    def test_creates_morning_message_configuration(self):
        service = ParticipantService(username="test")
        service.initialize()

        configuration = MorningMessageConfiguration.objects.get()
        self.assertEqual(configuration.user.username, "test")

    def test_creates_anti_sedentary_configuration(self):
        service = ParticipantService(username="test")
        service.initialize()

        configuration = AntiSedentaryConfiguration.objects.get()
        self.assertEqual(configuration.user.username, "test")

    @patch.object(initialize_participant, 'send')
    def test_sends_initialize_participant_signal(self, initialize_participant):
        service = ParticipantService(participant = self.participant)
        service.initialize()

        initialize_participant.assert_called_with(
            sender = Participant,
            participant = self.participant
        )
