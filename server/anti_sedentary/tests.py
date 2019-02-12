import pytz
from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from anti_seds.models import StepCount
from locations.services import LocationService
from push_messages.models import Device, Message
from push_messages.services import PushMessageService

from .models import AntiSedentaryDecision, AntiSedentaryMessageTemplate, User, Configuration
from .services import AntiSedentaryService, AntiSedentaryDecisionService
from .tasks import make_decision, start_decision

class TestBase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )

        push_service_patch = patch.object(PushMessageService, 'send_notification')
        self.addCleanup(push_service_patch.stop)
        self.send_notification = push_service_patch.start()
        self.send_notification.return_value = Message.objects.create(
            recipient = self.user,
            content = "foo"
        )
        Device.objects.create(
            user = self.user,
            active = True
        )

        message_template = AntiSedentaryMessageTemplate.objects.create(
            body = "Example message"
        )
        message_template.add_context("evening")

        weather_context_patch = patch.object(AntiSedentaryDecisionService, 'get_weather_context')
        self.addCleanup(weather_context_patch.stop)
        self.weather_context = weather_context_patch.start()
        self.weather_context.return_value = "outside"

        location_context_patch = patch.object(AntiSedentaryDecisionService, 'get_weather_context')
        self.addCleanup(location_context_patch.stop)
        self.location_context = location_context_patch.start()
        self.location_context.return_value = "home"

        week_context_patch = patch.object(AntiSedentaryDecisionService, 'get_week_context')
        self.addCleanup(week_context_patch.stop)
        self.week_context = week_context_patch.start()
        self.week_context.return_value = "weekday"

        location_service_patch = patch.object(LocationService, 'get_timezone_on')
        self.addCleanup(location_service_patch.stop)
        self.get_timezone_on = location_service_patch.start()
        self.get_timezone_on.return_value = pytz.timezone('Etc/GMT+8')

        self.local_timezone = pytz.timezone('Etc/GMT+8')
    
    def localize_time(self, time):
        return self.local_timezone.localize(time)

class AntiSedentaryDecisionServiceTest(TestBase):

    def test_available_during_day(self):
        decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 13, 30))
        )

        decision_service = AntiSedentaryDecisionService(decision)
        decision_service.update_availability()

        decision = AntiSedentaryDecision.objects.get(id=decision.id)
        self.assertTrue(decision.available)

    def test_set_morning_context(self):
        decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 10, 30))
        )
        decision_service = AntiSedentaryDecisionService(decision)

        decision_service.update_context()

        decision_context = decision.get_context()
        self.assertIn('morning', decision_context)
        self.assertNotIn('lunch', decision_context)

    def test_set_lunch_context(self):
        decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 12, 30))
        )
        decision_service = AntiSedentaryDecisionService(decision)

        decision_service.update_context()

        decision_context = decision.get_context()
        self.assertIn('lunch', decision_context)
        self.assertNotIn('morning', decision_context)
        self.assertNotIn('midafternoon', decision_context)

    def test_set_midafternoon_context(self):
        decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 15, 00))
        )
        decision_service = AntiSedentaryDecisionService(decision)

        decision_service.update_context()

        decision_context = decision.get_context()
        self.assertIn('midafternoon', decision_context)
        self.assertNotIn('lunch', decision_context)

    def test_set_evening_context(self):
        decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 17, 00))
        )
        decision_service = AntiSedentaryDecisionService(decision)

        decision_service.update_context()

        decision_context = decision.get_context()
        self.assertIn('evening', decision_context)
        self.assertNotIn('postdinner', decision_context)

    def test_set_postdinner_context(self):
        decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 20, 00))
        )
        decision_service = AntiSedentaryDecisionService(decision)

        decision_service.update_context()

        decision_context = decision.get_context()
        self.assertIn('postdinner', decision_context)

class StartDecisionTaskTest(TestBase):
    
    def setUp(self):
        super().setUp()

        now_patch = patch.object(timezone, 'now')
        self.now = now_patch.start()
        self.addCleanup(now_patch.stop)

        make_decision_patch = patch.object(make_decision, 'apply_async')
        self.make_decision = make_decision_patch.start()
        self.addCleanup(make_decision_patch.stop)

    def testRandomizesDuringDay(self):
        self.now.return_value = self.local_timezone.localize(datetime(2019, 1, 18, 14, 00))

        start_decision("test")

        decision = AntiSedentaryDecision.objects.get()
        self.assertEqual("test", decision.user.username)
        self.make_decision.assert_called_with(kwargs={
            'decision_id': str(decision.id)
        })

    def testDoesNotRandomizeBeforeDay(self):
        self.now.return_value = self.local_timezone.localize(datetime(2019, 1, 18, 7, 59))

        start_decision("test")

        self.assertEqual(AntiSedentaryDecision.objects.count(), 0)
        self.make_decision.assert_not_called()
    
    def testDoesNotRandomizeAfterDay(self):
        self.now.return_value = self.local_timezone.localize(datetime(2019, 1, 18, 20, 1))

        start_decision("test")

        self.assertEqual(AntiSedentaryDecision.objects.count(), 0)
        self.make_decision.assert_not_called()        


class MakeDecisionTests(TestBase):

    def setUp(self):
        super().setUp()

        self.decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 14, 00))
        )

        decision_decide_patch = patch.object(AntiSedentaryDecision, 'decide')
        self.addCleanup(decision_decide_patch.stop)
        self.decision_decide = decision_decide_patch.start()
        def mock_decide():
            self.decision.treated = True
            self.decision.treatment_probability = 1
            self.decision.save()
            return True
        self.decision_decide.side_effect = mock_decide

    def test_sends_anti_sedentary_message(self):
        make_decision(self.decision.id)

        self.send_notification.assert_called_with("Example message", title=None)

class DetermineSedentary(TestBase):

    def setUp(self):
        super().setUp()

        self.service = AntiSedentaryService(
            configuration=self.configuration
        )

        start_decision_mock = patch.object(start_decision, 'apply_async')
        start_decision_mock.start()
        self.addCleanup(start_decision_mock.stop)

    def create_step_count(self, time, steps):
        StepCount.objects.create(
            user = self.user,
            step_dtm = time,
            step_number = steps
        )

    def testNotSedentary(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))
        self.create_step_count(
            time = now,
            steps = 300
        )

        is_sedentary = self.service.is_sedentary_at(now)

        self.assertFalse(is_sedentary)

    def testSedentary(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))
        self.create_step_count(
            time = now - timedelta(minutes=5),
            steps = 180
        )
        self.create_step_count(
            time = now,
            steps = 100
        )

        is_sedentary = self.service.is_sedentary_at(now)

        self.assertTrue(is_sedentary)

    def testSedentaryWithNoSteps(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))
        
        is_sedentary = self.service.is_sedentary_at(now)

        self.assertFalse(is_sedentary)

    def testStepChangePositive(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))
        self.create_step_count(
            time = now - timedelta(minutes=5),
            steps = 20
        )
        self.create_step_count(
            time = now,
            steps = 100
        )

        step_change = self.service.get_step_count_change_at(now)

        self.assertEqual(step_change, 80)

    def testStepChangeNegative(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))
        self.create_step_count(
            time = now - timedelta(minutes=5),
            steps = 120
        )
        self.create_step_count(
            time = now,
            steps = 100
        )

        step_change = self.service.get_step_count_change_at(now)

        self.assertEqual(step_change, 0)

    def testStepChangeSingleStepCount(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))
        self.create_step_count(
            time = now,
            steps = 90
        )

        step_change = self.service.get_step_count_change_at(now)

        self.assertEqual(step_change, 90)

    def testStepChangeNoSteps(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))

        step_change = self.service.get_step_count_change_at(now)

        self.assertEqual(step_change, 0)
        
