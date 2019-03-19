from unittest.mock import patch
from datetime import datetime

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from walking_suggestions.models import SuggestionTime, Configuration, WalkingSuggestionDecision
from walking_suggestions.services import WalkingSuggestionDecisionService, WalkingSuggestionService
from walking_suggestions.tasks import start_decision, request_decision_context, make_decision


class StartTaskTests(TestCase):

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('walking_suggestions.tasks.request_decision_context.apply_async')
    def test_start_decision(self, request_decision_context):
        user = User.objects.create(username="test")
        SuggestionTime.objects.create(
            user=user,
            category = 'evening',
            hour = 20,
            minute = 00
        )

        start_decision(user.username, 'evening')

        decision = WalkingSuggestionDecision.objects.get(user=user)
        tags = [tag.tag for tag in decision.tags.all()]
        self.assertIn('evening', tags)
        request_decision_context.assert_called()

@override_settings(WALKING_SUGGESTION_REQUEST_RETRY_ATTEMPTS=1)
class RequestContextTaskTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        Configuration.objects.create(
            user = self.user
        )
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        self.decision_id = str(decision.id)

        patch_apply_async = patch.object(request_decision_context, 'apply_async')
        self.request_decision_context = patch_apply_async.start()
        self.addCleanup(patch_apply_async.stop)

        patch_make_decision = patch.object(make_decision, 'apply_async')
        self.make_decision = patch_make_decision.start()
        self.addCleanup(patch_make_decision.stop)

    @patch.object(WalkingSuggestionDecisionService, 'request_context')
    def test_requests_context(self, request_context):
        request_decision_context(
            decision_id = self.decision_id
        )

        request_context.assert_called()
        self.make_decision.assert_not_called()
        self.request_decision_context.assert_called()
        # Get fresh object, because decision not mutated.
        decision = WalkingSuggestionDecision.objects.get()
        self.assertTrue(decision.available)

    @patch.object(WalkingSuggestionDecisionService, 'get_context_requests', return_value=['foo', 'bar'])
    def test_request_context_makes_decision(self, get_context_requests):
        request_decision_context(
            decision_id = self.decision_id
        )

        self.make_decision.assert_called()
        self.request_decision_context.assert_not_called()
        # Get fresh object, because decision not mutated.
        decision = WalkingSuggestionDecision.objects.get()
        self.assertFalse(decision.available)
        self.assertEqual(decision.unavailable_reason, 'Unreachable')

    def raise_unreachable(self):
         raise WalkingSuggestionDecisionService.Unreachable('Sample error message')

    @patch.object(WalkingSuggestionDecisionService, 'request_context')
    def test_request_context_no_device(self, request_context):
        request_context.side_effect = self.raise_unreachable
        
        request_decision_context(
            decision_id = self.decision_id
        )

        self.make_decision.assert_called()
        decision = WalkingSuggestionDecision.objects.get()
        self.assertFalse(decision.available)
        self.assertEqual(decision.unavailable_reason, 'Sample error message')

class MakeDecisionTest(TestCase):

    def setUp(self):
        user = User.objects.create(username="test")
        Configuration.objects.create(
            user = user,
            enabled = True,
            service_initialized_date = timezone.now()
        )
        self.decision = WalkingSuggestionDecision.objects.create(
            user = user,
            time = timezone.now()
        )

        update_context_patch = patch.object(WalkingSuggestionDecisionService, 'update_context')
        self.addCleanup(update_context_patch.stop)
        self.update_context = update_context_patch.start()

        send_message_patch = patch.object(WalkingSuggestionDecisionService, 'send_message')
        self.addCleanup(send_message_patch.stop)
        self.send_message = send_message_patch.start()

    @patch.object(WalkingSuggestionDecisionService, 'decide', return_value=True)
    def test_decision_to_treat(self, decide):
        make_decision(str(self.decision.id))

        self.update_context.assert_called()
        decide.assert_called()
        self.send_message.assert_called()

    @patch.object(WalkingSuggestionDecisionService, 'decide', return_value=False)
    def test_decision_not_to_treat(self, decide):
        make_decision(str(self.decision.id))

        self.update_context.assert_called()
        decide.assert_called()
        self.send_message.assert_not_called()

    def raise_service_error(self):
        raise WalkingSuggestionService.RequestError('Walking suggestion service error')

    @override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example.com')
    @patch.object(WalkingSuggestionService, 'decide', side_effect=raise_service_error)
    def test_walking_suggestion_service_error(self, decide):
        make_decision(str(self.decision.id))

        decision = WalkingSuggestionDecision.objects.get()
        self.assertFalse(decision.treated)
        self.assertFalse(decision.available)
        self.assertEqual(decision.unavailable_reason, 'Walking suggestion service error')
