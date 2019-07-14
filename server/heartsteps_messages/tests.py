from unittest.mock import patch

from django.test import TestCase

from anti_sedentary.services import AntiSedentaryDecisionService
from walking_suggestions.services import WalkingSuggestionDecisionService
from watch_app.models import User
from watch_app.signals import step_count_updated

from .tasks import step_count_message_randomization

class WatchAppStepCountRandomizesMessages(TestCase):

    def setUp(self):

        anti_sedentary_patch = patch.object(AntiSedentaryDecisionService, 'make_decision_now')
        self.anti_sedentary_make_decision = anti_sedentary_patch.start()
        self.addCleanup(anti_sedentary_patch.stop)

        walking_suggestion_patch = patch.object(WalkingSuggestionDecisionService, 'make_decision_now')
        self.walking_suggestion_make_decision = walking_suggestion_patch.start()
        self.addCleanup(walking_suggestion_patch.stop)

    @patch.object(step_count_message_randomization, 'apply_async')
    def test_step_count_update_signal_runs_message_randomization(self, message_randomization):
        step_count_updated.send(
            sender = User,
            username = 'test'
        )

        message_randomization.assert_called_with(
            kwargs = {
                'username': 'test'
            }
        )

    def test_message_randomization_makes_decision(self):
        
        step_count_message_randomization(
            username = 'test'
        )

        self.walking_suggestion_make_decision.assert_called_with(
            username = 'test'
        )
        self.anti_sedentary_make_decision.assert_called_with(
            username = 'test'
        )

    def test_catch_walking_suggestion_randomization_unavialable(self):
        self.walking_suggestion_make_decision.side_effect = RuntimeError('test')
        try:
            step_count_message_randomization(username='test')
            self.fail('Should have failed')
        except RuntimeError:
            pass
        self.anti_sedentary_make_decision.assert_not_called()

        self.walking_suggestion_make_decision.side_effect = WalkingSuggestionDecisionService.RandomizationUnavailable('test')

        step_count_message_randomization(username='test')
        
        self.anti_sedentary_make_decision.assert_called_with(
            username = 'test'
        )

    def test_catch_anti_sedentary_randomization_unavailable(self):
        self.anti_sedentary_make_decision.side_effect = RuntimeError('Test')
        try:
            step_count_message_randomization(
                username = 'test'
            )
            self.fail('Should have failed')
        except RuntimeError:
            pass
        self.walking_suggestion_make_decision.assert_called_with(
            username = 'test'
        )

        self.anti_sedentary_make_decision.side_effect = AntiSedentaryDecisionService.RandomizationUnavailable('test')

        step_count_message_randomization(
            username='test'
        )
        
        self.assertEqual(self.walking_suggestion_make_decision.call_count, 2)


