from unittest.mock import patch
from datetime import datetime

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from randomization.models import Decision

from activity_suggestions.models import SuggestionTime
from activity_suggestions.services import ActivitySuggestionDecisionService, ActivitySuggestionService
from activity_suggestions.tasks import start_decision, make_decision, initialize_activity_suggestion_service


class TaskTests(TestCase):

    def test_initialize_activity_suggestion_service(self):
        pass

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('activity_suggestions.tasks.make_decision.apply_async')
    @patch('randomization.services.DecisionService.request_context')
    def test_start_decision(self, request_context, make_decision):
        user = User.objects.create(username="test")
        SuggestionTime.objects.create(
            user = user,
            type = 'evening',
            hour = 20,
            minute = 00
        )

        start_decision(user.username, 'evening')

        decision = Decision.objects.get(user=user)
        tags = [tag.tag for tag in decision.tags.all()]
        self.assertIn('activity suggestion', tags)
        self.assertIn('evening', tags)
        make_decision.assert_called()
        request_context.assert_called()

class MakeDecisionTest(TestCase):

    def setUp(self):
        user = User.objects.create(username="test")
        self.decision = Decision.objects.create(
            user = user,
            time = timezone.now()
        )

        update_context_patch = patch.object(ActivitySuggestionDecisionService, 'update_context')
        self.addCleanup(update_context_patch.stop)
        self.update_context = update_context_patch.start()

        create_message_patch = patch.object(ActivitySuggestionDecisionService, 'create_message')
        self.addCleanup(create_message_patch.stop)
        self.create_message = create_message_patch.start()

        send_message_patch = patch.object(ActivitySuggestionDecisionService, 'send_message')
        self.addCleanup(send_message_patch.stop)
        self.send_message = send_message_patch.start()

    @patch.object(ActivitySuggestionDecisionService, 'decide', return_value=True)
    def test_decision_to_treat(self, decide):
        make_decision(str(self.decision.id))

        self.update_context.assert_called()
        decide.assert_called()
        self.create_message.assert_called()
        self.send_message.assert_called()

    @patch.object(ActivitySuggestionDecisionService, 'decide', return_value=False)
    def test_decision_not_to_treat(self, decide):
        make_decision(str(self.decision.id))

        self.update_context.assert_called()
        decide.assert_called()
        self.create_message.assert_not_called()
        self.send_message.assert_not_called()

class InitializeTaskTests(TestCase):

    @patch.object(ActivitySuggestionService, 'initialize')
    def test_initialize(self, initialize):
        User.objects.create(username='test')

        initialize_activity_suggestion_service('test', '2018-10-15')

        initialize.assert_called_with(datetime(2018,10,15))
