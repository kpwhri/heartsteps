import pytz
from datetime import date
from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from days.services import DayService 
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from fitbit_clock_face.models import StepCount
from push_messages.models import Device, Message
from push_messages.services import PushMessageService
from walking_suggestion_times.models import SuggestionTime

from .clients import AntiSedentaryClient
from .models import AntiSedentaryDecision, AntiSedentaryMessageTemplate, User, Configuration
from .services import AntiSedentaryService, AntiSedentaryDecisionService

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

        day_service_patch = patch.object(DayService, 'get_timezone_at')
        self.addCleanup(day_service_patch.stop)
        self.get_timezone_on = day_service_patch.start()
        self.get_timezone_on.return_value = pytz.timezone('Etc/GMT+8')

        self.local_timezone = pytz.timezone('Etc/GMT+8')
    
    def localize_time(self, time):
        return self.local_timezone.localize(time)

class AntiSedentaryDecisionServiceSetContextTest(TestBase):

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

        process_decision_patch = patch.object(AntiSedentaryDecisionService, 'process_decision')
        self.process_decision = process_decision_patch.start()
        self.addCleanup(process_decision_patch.stop)

    def testRandomizesDuringDay(self):
        self.now.return_value = self.local_timezone.localize(datetime(2019, 1, 18, 14, 00))

        AntiSedentaryDecisionService.make_decision_now(username="test")

        decision = AntiSedentaryDecision.objects.get()
        self.assertEqual("test", decision.user.username)
        self.process_decision.assert_called()

    def testDoesNotRandomizeBeforeDay(self):
        self.now.return_value = self.local_timezone.localize(datetime(2019, 1, 18, 7, 59))

        try:
            AntiSedentaryDecisionService.make_decision_now(username="test")
            self.fail('Test should have failed')
        except AntiSedentaryDecisionService.RandomizationUnavailable:
            pass

        self.assertEqual(AntiSedentaryDecision.objects.count(), 0)
        self.process_decision.assert_not_called()
    
    def testDoesNotRandomizeAfterDay(self):
        self.now.return_value = self.local_timezone.localize(datetime(2019, 1, 18, 20, 1))

        try:
            AntiSedentaryDecisionService.make_decision_now(username="test")
            self.fail('Test should have failed')
        except AntiSedentaryDecisionService.RandomizationUnavailable:
            pass

        self.assertEqual(AntiSedentaryDecision.objects.count(), 0)
        self.process_decision.assert_not_called()        


class MakeDecisionTests(TestBase):

    def setUp(self):
        super().setUp()

        self.decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 14, 00))
        )

    def testUnavailableWhenActive(self):
        StepCount.objects.create(
            user = self.user,
            steps = 200,
            start = self.local_timezone.localize(datetime(2019, 1, 18, 13, 55)),
            end = self.local_timezone.localize(datetime(2019, 1, 18, 14, 00))
        )

        AntiSedentaryDecisionService.process_decision(self.decision)

        self.send_notification.assert_not_called()

        decision = AntiSedentaryDecision.objects.get()
        self.assertFalse(decision.sedentary)
        self.assertFalse(decision.available)
        self.assertTrue(decision.unavailable_not_sedentary)
        self.assertFalse(decision.treated)

    def testAvailableWhenSedentary(self):
        StepCount.objects.create(
            user = self.user,
            steps = 20,
            start = self.local_timezone.localize(datetime(2019, 1, 18, 13, 55)),
            end = self.local_timezone.localize(datetime(2019, 1, 18, 14, 00))
        )

        AntiSedentaryDecisionService.process_decision(self.decision)

        decision = AntiSedentaryDecision.objects.get()
        self.assertTrue(decision.sedentary)
        self.assertTrue(decision.available)

    def testSendNoClient(self):
        decision_decide_patch = patch.object(AntiSedentaryDecision, 'decide')
        self.addCleanup(decision_decide_patch.stop)
        self.decision_decide = decision_decide_patch.start()
        def mock_decide():
            self.decision.treated = True
            self.decision.treatment_probability = 1
            self.decision.save()
            return True
        self.decision_decide.side_effect = mock_decide

        AntiSedentaryDecisionService.process_decision(self.decision)

        self.send_notification.assert_called_with(
            "Example message",
            title='Been sitting for too long?',
            data={
                'randomizationId': str(self.decision.id)
            },
            collapse_subject = 'activity-suggestion'        
        )
    
    @override_settings(ANTI_SEDENTARY_SERVICE_URL='http://example')
    @patch.object(AntiSedentaryClient, 'make_request')
    def testSendWithClient(self, make_request):
        make_request.return_value = {
            'a_it': 1,
            'pi_it': 0.75
        }

        AntiSedentaryDecisionService.process_decision(self.decision)

        decision = AntiSedentaryDecision.objects.get()
        self.assertTrue(decision.treated)
        self.assertEqual(decision.treatment_probability, 0.75)
        self.send_notification.assert_called_with(
            "Example message",
            title='Been sitting for too long?',
            data={
                'randomizationId': str(self.decision.id)
            },
            collapse_subject = 'activity-suggestion'
        )

        make_request.assert_called_with(
            uri = 'decision',
            data = {
                'decisionid': str(self.decision.id),
                'time': '2019-01-18 14:00',
                'daystart': '2019-01-18 08:00',
                'dayend': '2019-01-18 20:00',
                'state': 0,
                'available': 0,
                'steps': 0
            }
        )

    @override_settings(ANTI_SEDENTARY_SERVICE_URL='http://example')
    @patch.object(AntiSedentaryClient, 'make_request')
    def test_send_to_client_with_offset_start_end_times(self, make_request):
        SuggestionTime.objects.create(
            user = self.user,
            hour = 22,
            minute = 15,
            category = SuggestionTime.POSTDINNER
        )
        make_request.return_value = {
            'a_it': 0,
            'pi_it': 0.123    
        }

        AntiSedentaryDecisionService.process_decision(self.decision)

        make_request.assert_called_with(
            uri='decision',
            data = {
                'decisionid': str(self.decision.id),
                'time': '2019-01-18 14:00',
                'daystart': '2019-01-18 11:15',
                'dayend': '2019-01-18 23:15',
                'state': 0,
                'available': 0,
                'steps':0
            }
        )


class DetermineSedentary(TestBase):

    def setUp(self):
        super().setUp()

        self.service = AntiSedentaryService(
            configuration=self.configuration
        )

    def create_step_count(self, time, steps):
        StepCount.objects.create(
            user = self.user,
            end = time,
            start = time - timedelta(minutes=5),
            steps = steps
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
            time = now - timedelta(minutes=45),
            steps = 180
        )
        self.create_step_count(
            time = now - timedelta(minutes=30),
            steps = 80
        )
        self.create_step_count(
            time = now,
            steps = 20
        )

        is_sedentary = self.service.is_sedentary_at(now)

        self.assertTrue(is_sedentary)

    def testSedentaryWithNoSteps(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))
        
        is_sedentary = self.service.is_sedentary_at(now)

        self.assertFalse(is_sedentary)

    def testStepCountChange(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))
        self.create_step_count(
            time = now - timedelta(minutes=20),
            steps = 120
        )
        self.create_step_count(
            time = now - timedelta(minutes=20),
            steps = 12
        )
        self.create_step_count(
            time = now,
            steps = 30
        )

        step_change = self.service.get_step_count_change_at(now)

        self.assertEqual(step_change, 30)

    def testStepChangeNoSteps(self):
        now = self.localize_time(datetime(2019, 1, 18, 14, 0))

        step_change = self.service.get_step_count_change_at(now)

        self.assertEqual(step_change, 0)


@override_settings(ANTI_SEDENTARY_SERVICE_URL='http://example')
class UpdateAntiSedentaryService(TestBase):

    def setUp(self):
        super().setUp()

        FitbitAccountUser.objects.create(
            user = self.user,
            account = FitbitAccount.objects.create(
                fitbit_user = 'test'
            )
        )

        make_request_mock = patch.object(AntiSedentaryClient, 'make_request')
        self.make_request = make_request_mock.start()
        self.make_request.return_value = None
        self.addCleanup(make_request_mock.stop)

    def testUpdate(self):
        service = AntiSedentaryService(
            configuration = self.configuration
        )
        today = date(2019, 1, 18)

        service.update(today)

        self.assertEqual(self.make_request.call_count, 145)
        self.assertEqual(AntiSedentaryDecision.objects.count(), 145)
