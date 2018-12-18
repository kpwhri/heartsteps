from django.urls import reverse
from django.utils import timezone

from unittest.mock import patch
from django.test import override_settings, TestCase

from django.contrib.auth.models import User

from behavioral_messages.models import ContextTag as MessageTag, MessageTemplate
from push_messages.models import Message as PushMessage, Device
from push_messages.services import PushMessageService

from randomization.models import Decision, DecisionContext
from randomization.services import DecisionMessageService

class DecisionMessageTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

    def make_decision_service(self):
        decision = Decision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        return DecisionMessageService(decision)

    def test_decision_picks_message_template(self):
        decision_service = self.make_decision_service()
        message_template = MessageTemplate.objects.create(body="Test message")

        message = decision_service.create_message_template()

        self.assertEqual(message.body, message_template.body)

    def test_decision_picks_message_template_with_matching_tags(self):
        tag = MessageTag.objects.create(tag="tag")

        message_template = MessageTemplate.objects.create(body="Test message")
        message_template.context_tags.add(tag)

        MessageTemplate.objects.create(body="Not this message")

        decision_service = self.make_decision_service()
        decision_service.add_context("tag")
        
        message = decision_service.create_message_template()

        self.assertNotEqual(message.body, "Not this message")

    def test_decision_picks_most_specific_matching_template(self):
        tag = MessageTag.objects.create(tag="tag")
        specific_tag = MessageTag.objects.create(tag="specific tag")

        template = MessageTemplate.objects.create(body="Test message")
        template.context_tags.add(tag)

        specific_template = MessageTemplate.objects.create(body="Specific test message")
        specific_template.context_tags.add(tag, specific_tag)

        MessageTemplate.objects.create(body="Generic message")
        MessageTemplate.objects.create(body="Generic message 2")

        decision_service = self.make_decision_service()
        decision_service.add_context("tag")
        decision_service.add_context("specific tag")
        
        message = decision_service.create_message_template()

        self.assertEqual(message.body, specific_template.body)

    def test_decision_ignores_context_that_is_not_message_tag(self):
        tag = MessageTag.objects.create(tag="tag")
        template = MessageTemplate.objects.create(body="Test message")
        template.context_tags.add(tag)

        decision_service = self.make_decision_service()
        decision_service.add_context("tag")
        decision_service.add_context("not a message tag")
        
        message = decision_service.create_message_template()

        self.assertEqual(message.body, "Test message")

    @patch.object(PushMessageService, 'send_notification')
    def test_sends_message(self, send_notification):
        decision_service = self.make_decision_service()
        Device.objects.create(
            user = self.user,
            active = True,
            token ="123"
        )
        message_template = MessageTemplate.objects.create(body="Test message")
        push_message = PushMessage.objects.create(
            recipient = self.user,
            content = "foo",
            message_type = PushMessage.NOTIFICATION
        )
        send_notification.return_value = push_message

        decision_service.send_message()

        send_notification.assert_called_with(message_template.body, title=message_template.title)

        context_objects = [obj.content_object for obj in DecisionContext.objects.all()]
        self.assertIn(message_template, context_objects)
        self.assertIn(push_message, context_objects)