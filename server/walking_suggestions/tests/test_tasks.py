import pytz
from unittest.mock import patch
from datetime import datetime, date, timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser

from walking_suggestions.models import SuggestionTime, Configuration, WalkingSuggestionDecision, NightlyUpdate
from walking_suggestions.services import WalkingSuggestionDecisionService, WalkingSuggestionService
from walking_suggestions.tasks import nightly_update
from walking_suggestions.tasks import initialize_and_update

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

        process_decision_patch = patch.object(WalkingSuggestionDecisionService, 'process_decision')
        self.process_decision = process_decision_patch.start()
        self.addCleanup(process_decision_patch.stop)

    # def testDoesNotMakeDecisionIfNotConfigured(self):
    #     self.configuration.enabled = False
    #     self.configuration.save()

    #     try:
    #         WalkingSuggestionDecisionService.make_decision_now(username='test')
    #         self.fail('Should have thrown exception')
    #     except WalkingSuggestionDecisionService.RandomizationUnavailable:
    #         pass

    #     self.assertEqual(WalkingSuggestionDecision.objects.count(), 0)
    #     self.process_decision.assert_not_called()

    @override_settings(WALKING_SUGGESTION_DECISION_WINDOW_MINUTES='5')
    def testDoesNotCreateDecisionIfNotCorrectTime(self):
        SuggestionTime.objects.create(
            user =self.user,
            category = SuggestionTime.LUNCH,
            hour = 11,
            minute = 0
        )

        # Before decision window
        self.now.return_value = datetime(2019, 4, 30, 10, 54).astimezone(pytz.UTC)
        try:
            WalkingSuggestionDecisionService.make_decision_now(username='test')
            self.fail('Should have thrown exception')
        except WalkingSuggestionDecisionService.RandomizationUnavailable:
            pass

        # After decision window
        self.now.return_value = datetime(2019, 4, 30, 11, 6).astimezone(pytz.UTC)
        try:
            WalkingSuggestionDecisionService.make_decision_now(username='test')
            self.fail('Should have thrown exception')
        except WalkingSuggestionDecisionService.RandomizationUnavailable:
            pass

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 0)
        self.process_decision.assert_not_called()

        # In decision window
        self.now.return_value = datetime(2019, 4, 30, 11, 3).astimezone(pytz.UTC)
        WalkingSuggestionDecisionService.make_decision_now(username='test')

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 1)
        self.process_decision.assert_called()

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
        WalkingSuggestionDecisionService.make_decision_now(username='test')

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 1)

        #Should not make new decision
        self.now.return_value = datetime(2019, 4, 30, 11, 3).astimezone(pytz.UTC)
        try:
            WalkingSuggestionDecisionService.make_decision_now(username='test')
            self.fail('Should have thrown exception')
        except WalkingSuggestionDecisionService.RandomizationUnavailable:
            pass

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 1)

        #New decision for midafternoon
        self.now.return_value = datetime(2019, 4, 30, 15, 30).astimezone(pytz.UTC)
        WalkingSuggestionDecisionService.make_decision_now(username='test')

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

        WalkingSuggestionDecisionService.make_decision_now(username='test')

        decision = WalkingSuggestionDecision.objects.get()
        self.assertEqual(decision.time, datetime_now)
        self.assertIn(SuggestionTime.EVENING, decision.get_context())
        self.process_decision.assert_called()

    @patch.object(DayService, 'get_timezone_at')
    def test_handles_timezones_correctly(self, get_timezone_at):
        tz = pytz.timezone('America/Los_Angeles')
        get_timezone_at.return_value = tz
        datetime_now = tz.localize(datetime(2019, 4, 30, 20, 4))
        self.now.return_value = datetime_now

        SuggestionTime.objects.create(
            user = self.user,
            category = SuggestionTime.EVENING,
            hour = 20,
            minute = 0
        )

        WalkingSuggestionDecisionService.make_decision_now(username='test')

        decision = WalkingSuggestionDecision.objects.get()
        self.assertEqual(decision.time, datetime_now)
        self.assertIn(SuggestionTime.EVENING, decision.get_context())
        self.process_decision.assert_called()

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
        WalkingSuggestionDecisionService.process_decision(self.decision)

        self.update_context.assert_called()
        decide.assert_called()
        self.send_message.assert_called()

    @patch.object(WalkingSuggestionDecisionService, 'decide', return_value=False)
    def test_decision_not_to_treat(self, decide):
        WalkingSuggestionDecisionService.process_decision(self.decision)

        self.update_context.assert_called()
        decide.assert_called()
        self.send_message.assert_not_called()

    def raise_service_error(self):
        raise WalkingSuggestionService.RequestError('Walking suggestion service error')

    @override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example.com')
    @patch.object(WalkingSuggestionService, 'decide', side_effect=raise_service_error)
    def test_walking_suggestion_service_error(self, decide):
        WalkingSuggestionDecisionService.process_decision(self.decision)

        decision = WalkingSuggestionDecision.objects.get()
        self.assertFalse(decision.treated)
        self.assertFalse(decision.available)
        self.assertTrue(decision.unavailable_service_error)

@override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example.com')
class NightlyUpdateTask(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username = 'test'
        )
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )

    @patch.object(WalkingSuggestionService, 'initialize')
    def testInitializeWalkingSuggestionService(self, initialize):
        self.configuration.service_initialized_date = None
        self.configuration.save()

        nightly_update(
            username=self.user.username,
            day_string = date.today().strftime('%Y-%m-%d')
        )

        initialize.assert_called_with(date=date.today())

    @patch.object(WalkingSuggestionService, 'update')
    def testUpdateWalkingSuggestionService(self, update):
        self.configuration.service_initialized_date = date.today() - timedelta(days=1)
        self.configuration.save()

        nightly_update(
            username = self.user.username,
            day_string = date.today().strftime('%Y-%m-%d')
        )

        update.assert_called_with(
            date = date.today()
        )
        update.assert_called_once()
        nightly_update_object = NightlyUpdate.objects.get()
        self.assertEqual(nightly_update_object.day, date.today())
        self.assertTrue(nightly_update_object.updated)

    @patch.object(WalkingSuggestionService, 'update')
    def testUpdateUnupdatedDays(self, update):
        self.configuration.service_initialized_date = date.today() - timedelta(days=4)
        self.configuration.save()
        NightlyUpdate.objects.create(
            user = self.user,
            day = date.today() - timedelta(days=3),
            updated = True
        )

        nightly_update(
            username = self.user.username,
            day_string = date.today().strftime('%Y-%m-%d')
        )

        self.assertEqual(update.call_count, 3)
        for day in [date.today() - timedelta(days=offset) for offset in range(3)]:
            update.assert_any_call(date=day)

@override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example.com')
@override_settings(WALKING_SUGGESTION_INITIALIZATION_DAYS=3)
class InitializeAndUpdateTaskTests(TestCase):

    @patch.object(FitbitDay, 'get_wore_fitbit', return_value=True)
    @patch.object(WalkingSuggestionService, 'initialize')
    @patch.object(WalkingSuggestionService, 'update')
    def test_initialize_and_update(self, update, initialize, get_wore_fitbit):
        user = User.objects.create(
            username = 'test',
            date_joined = timezone.now() - timedelta(days=10)
        )
        configuration = Configuration.objects.create(
            user = user,
            enabled = True
        )
        account = FitbitAccount.objects.create(fitbit_user='test')
        FitbitAccountUser.objects.create(
            account = account,
            user = user
        )
        for offset in range(7):
            FitbitDay.objects.create(
                account = account,
                date = date.today() - timedelta(days=offset)
            )

        initialize_and_update(username='test')

        initialize.assert_called_with(date.today() - timedelta(days=4))
        self.assertEqual(update.call_count, 3)
        self.assertEqual(NightlyUpdate.objects.count(), 3)

