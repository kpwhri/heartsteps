from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from locations.services import LocationService

from walking_suggestions.models import WalkingSuggestionDecision, SuggestionTime, User
from walking_suggestions.services import WalkingSuggestionDecisionService
from walking_suggestions.tasks import make_decision

class WalkingSuggestionCreateTest(APITestCase):
    
    @patch.object(WalkingSuggestionDecisionService, 'update_context')
    @patch.object(WalkingSuggestionDecisionService, 'decide')
    @patch.object(WalkingSuggestionDecisionService, 'send_message')
    def test_create(self, send_message, decide, update_context):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('walking-suggestions-create'), {
            'category': SuggestionTime.MORNING
        }, format='json')

        self.assertEqual(response.status_code, 201)
        update_context.assert_called()
        decide.assert_called()
        send_message.assert_called()
        
        decision = WalkingSuggestionDecision.objects.get()
        self.assertEqual(user, decision.user)
        self.assertTrue(decision.test)
