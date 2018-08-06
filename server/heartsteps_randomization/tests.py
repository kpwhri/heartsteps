from django.urls import reverse

from unittest.mock import patch
from django.test import override_settings, TestCase

from heartsteps_randomization.models import Decision, Location
from django.contrib.auth.models import User

from heartsteps_messages.models import ContextTag, MessageTemplate

from heartsteps_randomization.tasks import make_decision

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

class DecisionView(APITestCase):
    
    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('heartsteps_randomization.tasks.make_decision.delay')
    def test_creates_decision(self, make_decision):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('heartsteps-decisions-create'))
        
        self.assertEqual(response.status_code, 201)

        decision = Decision.objects.get(user=user, a_it=None)
        
        self.assertIsNotNone(decision)
        make_decision.assert_called()

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('heartsteps_randomization.tasks.make_decision.delay')
    def test_updates_decision(self, make_decision):
        user = User.objects.create(username="test")

        decision = Decision.objects.create(
            user = user
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('heartsteps-decisions-update', kwargs = {
            'decision_id': decision.id
        }))

        self.assertEqual(response.status_code, 200)
        make_decision.assert_called()


class DecisionTest(TestCase):

    def test_decision_picks_message_template(self):
        message_template = MessageTemplate.objects.create(body="Test message")

        decision = Decision.objects.create(
            user = User.objects.create(username="test")
        )

        decision.make_message()

        self.assertEqual(decision.message.body, message_template.body)

    def test_decision_picks_message_template_with_matching_tags(self):
        tag = ContextTag.objects.create(tag="tag")

        message_template = MessageTemplate.objects.create(body="Test message")
        message_template.context_tags.add(tag)

        message_template = MessageTemplate.objects.create(body="Other test message")
        message_template.context_tags.add(tag)

        MessageTemplate.objects.create(body="Not this message")

        decision = Decision.objects.create(
            user = User.objects.create(username="test")
        )
        decision.add_context("tag")

        decision.make_message()

        self.assertNotEqual(decision.message.body, "Not this message")

    def test_decision_picks_most_specific_matching_template(self):
        tag = ContextTag.objects.create(tag="tag")
        specific_tag = ContextTag.objects.create(tag="specific tag")

        template = MessageTemplate.objects.create(body="Test message")
        template.context_tags.add(tag)

        specific_template = MessageTemplate.objects.create(body="Specific test message")
        specific_template.context_tags.add(tag, specific_tag)

        MessageTemplate.objects.create(body="Generic message")
        MessageTemplate.objects.create(body="Generic message 2")

        decision = Decision.objects.create(
            user = User.objects.create(username="test")
        )
        decision.add_context("tag")
        decision.add_context("specific tag")

        decision.make_message()

        self.assertEqual(decision.message.body, specific_template.body)


class MakeDecisionTestCase(TestCase):

    @patch('heartsteps_randomization.models.Decision.get_context')
    def test_make_decision_gets_context(self, get_context):
        decision = Decision.objects.create(
            user = User.objects.create(username="test")
        )

        make_decision(str(decision.id))
        
        get_context.assert_called()

    @patch('heartsteps_randomization.models.Decision.decide', return_value=False)
    @patch('weather.functions.WeatherFunction.get_context', return_value=(42, "outdoor"))
    def test_make_decision_with_locaction(self, decision_decide, weather_function):
        decision = Decision.objects.create(
            user = User.objects.create(username="test")
        )
        pie_bar = Location.objects.create(
            decision = decision,
            lat = 47.6166953,
            long = -122.3273954
        )

        make_decision(str(decision.id))

        # Reload since task doesn't mutate object...
        decision = Decision.objects.first()

        self.assertIn('other', [tag.tag for tag in decision.tags.all()])
        self.assertIn('outdoor', [tag.tag for tag in decision.tags.all()])

        decision_decide.assert_called()
        weather_function.assert_called()





