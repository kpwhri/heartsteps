from unittest.mock import patch

from django.test import TestCase, override_settings

from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration

from participants.models import Participant, User
from participants.tasks import initialize_participant

class InitializeTask(TestCase):
    
    def test_creates_walking_suggestion_configuration(self):
        Participant.objects.create(
            user = User.objects.create(username="test")
        )

        initialize_participant("test")

        configuration = WalkingSuggestionConfiguration.objects.get(user__username="test")
        self.assertIsNotNone(configuration)
