from unittest.mock import patch
from datetime import datetime

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from walking_suggestions.models import SuggestionTime, Configuration, WalkingSuggestionDecision
from walking_suggestions.services import WalkingSuggestionDecisionService, WalkingSuggestionService
from walking_suggestions.tasks import start_decision, request_decision_context, make_decision, initialize_walking_suggestion_service, update_walking_suggestion_service


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
            user = self.user,
            impute_context = True
        )
        self.decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )

        patch_apply_async = patch.object(request_decision_context, 'apply_async')
        self.apply_async = patch_apply_async.start()
        self.addCleanup(patch_apply_async.stop)

    @patch.object(WalkingSuggestionDecisionService, 'request_context')
    def test_requests_context(self, request_context):
        request_decision_context(
            decision_id = str(self.decision.id)
        )

        request_context.assert_called()
        self.apply_async.assert_called()

    @patch.object(WalkingSuggestionDecisionService, 'get_context_requests', return_value=['foo', 'bar'])
    @patch.object(make_decision, 'apply_async')
    def test_request_context_makes_decision(self, make_decision, get_context_requests):
        request_decision_context(
            decision_id = str(self.decision.id)
        )

        make_decision.assert_called()


class MakeDecisionTest(TestCase):

    def setUp(self):
        user = User.objects.create(username="test")
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

class InitializeTaskTests(TestCase):

    @override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example.com')
    @patch.object(WalkingSuggestionService, 'initialize')
    def test_initialize(self, initialize):
        Configuration.objects.create(
            user = User.objects.create(username='test')
        )

        initialize_walking_suggestion_service('test')

        initialize.assert_called()

class NightlyUpdateTaskTests(TestCase):
    
    @override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example.com')
    @patch.object(WalkingSuggestionService, 'update', return_value="None")
    def test_update(self, update):
        Configuration.objects.create(
            user = User.objects.create(username='test')
        )

        update_walking_suggestion_service('test')

        update.assert_called()
