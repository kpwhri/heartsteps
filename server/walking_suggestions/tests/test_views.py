from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from locations.services import LocationService

from walking_suggestions.models import WalkingSuggestionDecision, SuggestionTime, User
from walking_suggestions.services import WalkingSuggestionDecisionService
from walking_suggestions.tasks import make_decision

class WalkingSuggestionCreateTest(APITestCase):
    
    @patch.object(WalkingSuggestionDecisionService, 'request_context')
    def test_create(self, request_context):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('walking-suggestions-create'), {
            'category': SuggestionTime.MORNING
        }, format='json')

        self.assertEqual(response.status_code, 201)
        request_context.assert_called()
        
        decision = WalkingSuggestionDecision.objects.get()
        self.assertEqual(user, decision.user)
        self.assertTrue(decision.test)


class WalkingSuggestionContextUpdate(APITestCase):

    def setUp(self):
        self.user = User.objects.create()
        self.client.force_authenticate(user=self.user)

        patch_make_decision = patch.object(make_decision, 'apply_async')
        self.make_decision = patch_make_decision.start()
        self.addCleanup(patch_make_decision.stop)

    def test_makes_decision_no_payload(self):
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )

        response = self.client.post(reverse('walking-suggestions-context', kwargs={
            'decision_id': str(decision.id)
        }))

        self.assertEqual(response.status_code, 200)
        self.make_decision.assert_called()

    @patch.object(LocationService, 'update_location')
    @patch.object(WalkingSuggestionDecision, 'add_context_object')
    def test_accepts_location(self, add_context_object, update_location):
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        location_object = {
            'latitude': 10,
            'longitude': 123
        }
        update_location.return_value = 'example'

        response = self.client.post(
            reverse('walking-suggestions-context', kwargs={
                'decision_id': str(decision.id)
            }), {
                'location': location_object
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.make_decision.assert_called()
        update_location.called_with(location_object)
        add_context_object.called_with('example')
