from unittest.mock import patch
from datetime import date

from django.test import TestCase

from push_messages.services import PushMessageService, Device, Message

from morning_messages.models import Configuration, DailyTask, MorningMessage, MorningMessageDecision, MorningMessageTemplate, User
from morning_messages.services import MorningMessageService, MorningMessageDecisionService
from morning_messages.tasks import send_morning_message

class MorningMessageTestBase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.configuration = Configuration.objects.create(user=self.user)

        Device.objects.create(
            user = self.user,
            active = True
        )
        patch_send_data = patch.object(PushMessageService, 'send_data')
        self.send_data = patch_send_data.start()
        self.send_data.return_value = Message.objects.create(
            recipient = self.user,
            content = "foo"
        )
        self.addCleanup(patch_send_data.stop)

        MorningMessageTemplate.objects.create(
            body = 'Example morning message',
            anchor_message = 'Anchor message'
        )

class MorningMessageConfigurationTest(MorningMessageTestBase):

    def test_daily_task_created_when_morning_message_created(self):
        self.assertIsNotNone(self.configuration.daily_task)
        self.assertTrue(self.configuration.daily_task.enabled)

    def test_daily_task_can_be_disabled(self):
        self.assertTrue(self.configuration.daily_task.enabled)

        self.configuration.enabled = False
        self.configuration.save()

        self.assertFalse(self.configuration.daily_task.enabled)

    def test_daily_task_destroyed_with_configuration(self):
        self.assertIsNotNone(self.configuration.daily_task)

        self.configuration.delete()

        self.assertEqual(0, DailyTask.objects.count())

class MorningMessageServiceTest(MorningMessageTestBase):

    def setUp(self):
        super().setUp()
        self.morning_message_service = MorningMessageService(
            configuration = self.configuration
        )
        self.morning_message_service.create(date(2019, 1, 15))

    def test_get_morning_message(self):
        morning_message = self.morning_message_service.get(date(2019, 1, 15))

        self.assertEqual(morning_message.user, self.user)
        self.assertEqual(morning_message.date, date(2019, 1, 15))

    def test_get_morning_message_does_not_exist(self):
        try:
            morning_message = self.morning_message_service.get(date(2019, 1, 16))
        except MorningMessageService.MessageDoesNotExist:
            morning_message = False
        self.assertFalse(morning_message)

    def test_create_morning_message(self):
        morning_message = self.morning_message_service.create(date(2019, 1, 16))

        self.assertEqual(morning_message.user, self.user)
        self.assertEqual(morning_message.date, date(2019, 1, 16))
        self.assertIsNotNone(morning_message.message_decision)
        self.assertTrue(morning_message.message_decision.treated)
        self.assertEqual(morning_message.message_decision.treatment_probability, 1)

    def test_morning_message_log_matches_morning_message_decision(self):
        self.morning_message_service.update_message(date(2019, 1, 15), None)

        morning_message = self.morning_message_service.get(date(2019, 1 , 15))
        self.assertEqual(morning_message.notification, 'Good Morning')
        self.assertIsNone(morning_message.text)
        self.assertIsNone(morning_message.anchor)

        MorningMessageTemplate.objects.create(
            body = "Example morning message",
            anchor_message = "Anchor message"
        )

        self.morning_message_service.update_message(date(2019, 1, 15), MorningMessageDecision.FRAME_GAIN_ACTIVE)
        
        morning_message = self.morning_message_service.get(date(2019, 1 , 15))
        self.assertEqual(morning_message.notification, 'Example morning message')
        self.assertEqual(morning_message.text, 'Example morning message')
        self.assertEqual(morning_message.anchor, 'Anchor message')

class MorningMessageTaskTest(MorningMessageTestBase):

    def test_creates_morning_message(self):
        send_morning_message(username="test")

        self.send_data.assert_called()
        
        morning_message = MorningMessage.objects.get()
        self.assertEqual(morning_message.user, self.user)
        self.assertEqual(morning_message.date, date.today())

    def test_disabled_task_state(self):
        self.configuration.enabled = False
        self.configuration.save()

        send_morning_message(username="test")

        self.send_data.assert_not_called()

        morning_message = MorningMessage.objects.get()
        self.assertEqual(morning_message.user, self.user)
        self.assertEqual(morning_message.date, date.today())

    @patch.object(MorningMessageDecision, 'get_random_message_frame', return_value=None)
    def test_message_with_no_framing(self, _):
        send_morning_message(username="test")

        self.send_data.assert_called()
        sent_data = self.send_data.call_args[0][0]
        self.assertEqual(sent_data['body'], 'Good Morning')
        assert 'text' not in sent_data
        assert 'anchor' not in sent_data

    @patch.object(MorningMessageDecision, 'get_random_message_frame', return_value=MorningMessageDecision.FRAME_GAIN_ACTIVE)
    def test_message_with_framing(self, _):
        send_morning_message(username="test")

        self.send_data.assert_called()
        sent_data = self.send_data.call_args[0][0]
        self.assertEqual(sent_data['body'], 'Example morning message')
        self.assertEqual(sent_data['text'], 'Example morning message')
        self.assertEqual(sent_data['anchor'], 'Anchor message')
