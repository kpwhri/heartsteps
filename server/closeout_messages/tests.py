from datetime import date
from datetime import timedelta
from django.test import TestCase
from unittest.mock import patch

from sms_messages.models import Contact
from sms_messages.models import Message
from sms_messages.services import SMSService

from .models import CLOSEOUT_MESSAGE
from .models import Configuration
from .models import User

class CloseoutMessageConfigurationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='test'
        )
        self.configuration = Configuration.objects.create(
            user = self.user,
            closeout_date = date.today()
        )
        self.configuration.enable()

        contact = Contact.objects.create(
            user = self.user,
            number = 5555555555
        )
        sms_service_send_patch = patch.object(SMSService, 'send')
        self.addCleanup(sms_service_send_patch.stop)
        self.sms_message_service_send = sms_service_send_patch.start()
        self.sms_message_service_send.return_value = Message.objects.create(
            recipient = 555,
            sender = 556,
            body = CLOSEOUT_MESSAGE
        )

    def test_configuration_active_with_daily_task(self):
        
        self.configuration.enable()

        configuration = Configuration.objects.get(user = self.user)
        self.assertTrue(configuration.enabled)
        self.assertTrue(configuration.daily_task.enabled)
        self.assertEqual(configuration.daily_task.hour, 19)

    def test_configuration_can_disable_daily_task(self):
        
        self.configuration.disable()

        configuration = Configuration.objects.get(user = self.user)
        self.assertFalse(configuration.enabled)
        self.assertFalse(configuration.daily_task.enabled)

    def test_sending_message_disables_daily_task(self):

        self.configuration.send_message()

        self.assertEqual(self.configuration.message.body, CLOSEOUT_MESSAGE)
        self.sms_message_service_send.assert_called_with(CLOSEOUT_MESSAGE)
        self.assertFalse(self.configuration.enabled)

    def test_will_not_send_message_if_task_disabled(self):
        
        self.configuration.disable()
        try:
            self.configuration.send_message()
            self.fail('Should not have passed')
        except Configuration.ConfigurationDisabled:
            pass
        self.sms_message_service_send.assert_not_called()

    def test_will_not_send_if_message_already_sent(self):
        self.configuration.enable()
        self.configuration.message = Message.objects.create(
            recipient = 123,
            sender = 456
        )
        self.configuration.save()

        try:
            self.configuration.send_message()
            self.fail('Should not have passed')
        except Configuration.MessageAlreadySent:
            pass
        self.sms_message_service_send.assert_not_called()

    def test_will_not_send_if_before_send_date(self):
        self.configuration.enable()
        self.configuration.closeout_date = date.today() + timedelta(days=3)
        self.configuration.save()

        try:
            self.configuration.send_message()
            self.fail('Should have failed')
        except Configuration.BeforeCloseoutDate:
            pass
        self.sms_message_service_send.assert_not_called()

    def test_will_not_send_if_configuration_user_is_disabled(self):
        self.user.is_active = False
        self.user.save()

        try:
            self.configuration.send_message()
            self.fail('Should have failed')
        except Configuration.ConfigurationDisabled:
            pass
        self.sms_message_service_send.assert_not_called()
