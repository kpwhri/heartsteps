import pytz
from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from locations.services import LocationService
from push_messages.models import Device, Message
from push_messages.services import PushMessageService

from .models import AntiSedentaryDecision, AntiSedentaryMessageTemplate, User
from .services import AntiSedentaryDecisionService
from .tasks import make_decision

class TestBase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

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

class AntiSedentaryDecisionServiceTest(TestBase):

    def setUp(self):
        super().setUp()
        
        location_service_patch = patch.object(LocationService, 'get_timezone_on')
        self.addCleanup(location_service_patch.stop)
        self.get_timezone_on = location_service_patch.start()
        self.get_timezone_on.return_value = pytz.timezone('Etc/GMT+8')

        self.local_timezone = pytz.timezone('Etc/GMT+8')

    def test_not_available_after_8pm(self):
        decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 20, 1)) 
        )

        decision_service = AntiSedentaryDecisionService(decision)
        decision_service.update_availability()

        decision = AntiSedentaryDecision.objects.get(id=decision.id)
        self.assertFalse(decision.available)

    def test_not_available_before_8am(self):
        decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = self.local_timezone.localize(datetime(2019, 1, 18, 7, 59))
        )

        decision_service = AntiSedentaryDecisionService(decision)
        decision_service.update_availability()

        decision = AntiSedentaryDecision.objects.get(id=decision.id)
        self.assertFalse(decision.available)

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

class AntiSedentaryMessageMakeDecisionTests(TestBase):

    def setUp(self):
        super().setUp()

        self.decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = timezone.now()
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
