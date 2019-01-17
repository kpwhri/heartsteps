from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from push_messages.models import Device, Message
from push_messages.services import PushMessageService

from .models import AntiSedentaryDecision, AntiSedentaryMessageTemplate, User
from .tasks import make_decision

class AntiSedentaryMessageMakeDecisionTests(TestCase):

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

        decision_decide_patch = patch.object(AntiSedentaryDecision, 'decide')
        self.addCleanup(decision_decide_patch.stop)
        self.decision_decide = decision_decide_patch.start()
        def mock_decide():
            self.decision.treated = True
            self.decision.treatment_probability = 1
            self.decision.save()
            return True
        self.decision_decide.side_effect = mock_decide

        message_template = AntiSedentaryMessageTemplate.objects.create(
            body = "Example message"
        )
        message_template.add_context("evening")


        self.decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )

    def test_sends_anti_sedentary_message(self):
        make_decision(self.decision.id)

        self.send_notification.assert_called_with("Example message", title=None)
