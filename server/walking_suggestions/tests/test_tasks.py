import pytz
from unittest.mock import patch
from datetime import datetime

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from walking_suggestions.models import SuggestionTime, Configuration, WalkingSuggestionDecision
from walking_suggestions.services import WalkingSuggestionDecisionService, WalkingSuggestionService
from walking_suggestions.tasks import create_decision, start_decision, make_decision

@override_settings(WALKING_SUGGESTION_DECISION_WINDOW_MINUTES='10')
class CreateDecisionTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.configuration = Configuration.objects.create(
            user=self.user,
            enabled=True
        )

        now_patch = patch.object(timezone, 'now')
        self.now = now_patch.start()
        self.addCleanup(now_patch.stop)

        make_decision_patch = patch.object(make_decision, 'apply_async')
        self.make_decision = make_decision_patch.start()
        self.addCleanup(make_decision_patch.stop)

    def testDoesNotMakeDecisionIfNotConfigured(self):
        self.configuration.enabled = False
        self.configuration.save()

        create_decision(username="test")

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 0)
        self.make_decision.assert_not_called()

    @override_settings(WALKING_SUGGESTION_DECISION_WINDOW_MINUTES='5')
    def testDoesNotCreateDecisionIfNotCorrectTime(self):
        SuggestionTime.objects.create(
            user =self.user,
            category = SuggestionTime.LUNCH,
            hour = 11,
            minute = 0
        )

        # Before decision window minutes
        self.now.return_value = datetime(2019, 4, 30, 10, 59).astimezone(pytz.UTC)
        create_decision(username="test")

        # Before decision window minutes
        self.now.return_value = datetime(2019, 4, 30, 11, 6).astimezone(pytz.UTC)
        create_decision(username="test")

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 0)
        self.make_decision.assert_not_called()

        # Before decision window minutes
        self.now.return_value = datetime(2019, 4, 30, 11, 3).astimezone(pytz.UTC)
        create_decision(username="test")

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 1)
        self.make_decision.assert_called()

    def testDoesNotCreateMultipleDecisionsOfSameType(self):
        SuggestionTime.objects.create(
            user =self.user,
            category = SuggestionTime.LUNCH,
            hour = 11,
            minute = 0
        )
        SuggestionTime.objects.create(
            user = self.user,
            category = SuggestionTime.MIDAFTERNOON,
            hour = 15,
            minute = 30
        )

        self.now.return_value = datetime(2019, 4, 30, 11).astimezone(pytz.UTC)
        create_decision(username="test")

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 1)

        #Should not make new decision
        self.now.return_value = datetime(2019, 4, 30, 11, 3).astimezone(pytz.UTC)
        create_decision(username="test")

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 1)

        #New decision for midafternoon
        self.now.return_value = datetime(2019, 4, 30, 15, 30).astimezone(pytz.UTC)
        create_decision(username="test")

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 2)


    def testCreateDecision(self):
        datetime_now = datetime(2019, 4, 30, 20, 0).astimezone(pytz.UTC)
        self.now.return_value = datetime_now

        SuggestionTime.objects.create(
            user = self.user,
            category = SuggestionTime.EVENING,
            hour = 20,
            minute = 0
        )

        create_decision(username="test")

        decision = WalkingSuggestionDecision.objects.get()
        self.assertEqual(decision.time, datetime_now)
        self.assertIn(SuggestionTime.EVENING, decision.get_context())
        self.make_decision.assert_called_with(kwargs={
            'decision_id': str(decision.id)
        })


class StartTaskTests(TestCase):

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('walking_suggestions.tasks.make_decision.apply_async')
    def test_start_decision(self, make_decision):
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
        make_decision.assert_called()

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
