from django.urls import reverse
from django.utils import timezone

from unittest.mock import patch
from django.test import override_settings, TestCase

from randomization.models import Decision, Message, DecisionContext
from django.contrib.auth.models import User

from behavioral_messages.models import ContextTag as MessageTag, MessageTemplate
from locations.models import Location
from push_messages.models import Message as PushMessage
from weather.models import WeatherForecast

class DecisionContextTest(TestCase):

    def test_decision_adds_context(self):
        user = User.objects.create(username=True)

    @patch('randomization.models.determine_location_type')
    @patch('weather.functions.WeatherFunction.get_context')
    def test_make_decision(self, weather_context, determine_location_type):
        forecast = WeatherForecast.objects.create(
            latitude=123,
            longitude=456.456,
            time = timezone.now(),
            precip_probability = 0.1,
            temperature = 0.123,
            apparent_temperature = 123,
            wind_speed = 0,
            cloud_cover = 0,
        )
        determine_location_type.return_value = "home"
        weather_context.return_value = (forecast, "outdoor")
        user = User.objects.create(username="test")
        location = Location.objects.create(
            user = user,
            latitude = 123.123,
            longitude = 456.456,
            time = timezone.now()
        )

        decision = Decision.objects.create(
            user = user,
            time = timezone.now()
        )
        decision.add_location_context()

        determine_location_type.assert_called()
        weather_context.assert_called()
        self.assertIn('home', [tag.tag for tag in decision.tags.all()])
        self.assertIn('outdoor', [tag.tag for tag in decision.tags.all()])
        self.assertEqual(DecisionContext.objects.filter(decision=decision).count(), 2)

class DecisionMessageTest(TestCase):

    def test_decision_picks_message_template(self):
        message_template = MessageTemplate.objects.create(body="Test message")

        decision = Decision.objects.create(
            user = User.objects.create(username="test"),
            time = timezone.now()       
        )
        message = Message(
            decision = decision
        )
        decision_message_template = message.get_message_template()

        self.assertEqual(decision_message_template.body, message_template.body)

    def test_decision_picks_message_template_with_matching_tags(self):
        tag = MessageTag.objects.create(tag="tag")

        message_template = MessageTemplate.objects.create(body="Test message")
        message_template.context_tags.add(tag)

        MessageTemplate.objects.create(body="Not this message")

        decision = Decision.objects.create(
            user = User.objects.create(username="test"),
            time = timezone.now()
        )
        decision.add_context("tag")
        message = Message(decision=decision)
        decision_message_template = message.get_message_template()

        self.assertNotEqual(decision_message_template.body, "Not this message")

    def test_decision_picks_most_specific_matching_template(self):
        tag = MessageTag.objects.create(tag="tag")
        specific_tag = MessageTag.objects.create(tag="specific tag")

        template = MessageTemplate.objects.create(body="Test message")
        template.context_tags.add(tag)

        specific_template = MessageTemplate.objects.create(body="Specific test message")
        specific_template.context_tags.add(tag, specific_tag)

        MessageTemplate.objects.create(body="Generic message")
        MessageTemplate.objects.create(body="Generic message 2")

        decision = Decision.objects.create(
            user = User.objects.create(username="test"),
            time = timezone.now()
        )
        decision.add_context("tag")
        decision.add_context("specific tag")
        message = Message(decision=decision)
        decision_message_template = message.get_message_template()

        self.assertEqual(decision_message_template.body, specific_template.body)

    def test_decision_ignores_context_that_is_not_message_tag(self):
        tag = MessageTag.objects.create(tag="tag")
        template = MessageTemplate.objects.create(body="Test message")
        template.context_tags.add(tag)

        decision = Decision.objects.create(
            user = User.objects.create(username="test"),
            time = timezone.now()
        )
        decision.add_context("tag")
        decision.add_context("not a message tag")
        message = Message(decision=decision)
        decision_message_template = message.get_message_template()

        self.assertEqual(decision_message_template.body, "Test message")
