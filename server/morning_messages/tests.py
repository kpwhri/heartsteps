from unittest.mock import patch

from django.test import TestCase

from push_messages.services import PushMessageService, Device, Message

from morning_messages.models import Configuration, DailyTask, MorningMessageDecision, MorningMessageTemplate, User
from morning_messages.services import MorningMessageDecisionService

class MorningMessageConfigurationTest(TestCase):

    def test_daily_task_created_when_morning_message_created(self):

        configuration = Configuration.objects.create(
            user = User.objects.create(username="test"),
        )

        self.assertIsNotNone(configuration.daily_task)
        self.assertTrue(configuration.daily_task.enabled)

    def test_daily_task_can_be_disabled(self):
        configuration = Configuration.objects.create(
            user = User.objects.create(username="test")
        )

        self.assertTrue(configuration.daily_task.enabled)

        configuration.enabled = False
        configuration.save()

        self.assertFalse(configuration.daily_task.enabled)

    def test_daily_task_destroyed_with_configuration(self):
        configuration = Configuration.objects.create(
            user = User.objects.create(username="test")
        )

        self.assertIsNotNone(configuration.daily_task)

        configuration.delete()

        self.assertEqual(0, DailyTask.objects.count())

class MorningMessageServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.configuration = Configuration.objects.create(user=self.user)

        Device.objects.create(
            user = self.user,
            active = True
        )
        patch_send_notification = patch.object(PushMessageService, 'send_notification')
        self.send_notification = patch_send_notification.start()
        self.send_notification.return_value = Message.objects.create(
            recipient = self.user,
            content = "foo"
        )
        self.addCleanup(patch_send_notification.stop)

        patch_message_frame = patch.object(MorningMessageDecision, 'get_message_frame')
        self.message_frame = patch_message_frame.start()
        self.addCleanup(patch_message_frame.stop)

        MorningMessageTemplate.objects.create(
            body = 'Example morning message',
            anchor_message = 'Anchor message'
        )

    def test_configuration(self):
        service = MorningMessageDecisionService(username="test")

        self.assertEqual(service.user.username, "test")
        self.assertEqual(service.configuration, self.configuration)

    def test_send_default_message(self):
        self.message_frame.return_value = None
        service = MorningMessageDecisionService(username="test")

        service.send_message()

        self.send_notification.assert_called_with("Good Morning", title="Good Morning")

    def test_framed_message(self):
        self.message_frame.return_value = MorningMessageDecision.FRAME_GAIN_ACTIVE
        service = MorningMessageDecisionService(username="test")

        service.send_message()

        self.send_notification.assert_called_with("Example morning message", title=None)
