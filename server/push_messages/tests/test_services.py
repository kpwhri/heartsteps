from unittest.mock import patch
from django.test import TestCase
import requests

from django.contrib.auth.models import User

from push_messages.models import Message, Device, MessageReceipt
from push_messages.services import PushMessageService, ClientBase, FirebaseMessageService, DeviceMissingError

class TestPushMessageService(TestCase):

    def make_user(self):
        user = User.objects.create(username="test")
        Device.objects.create(
            user = user,
            token = 'example-token',
            type = 'android',
            active = True
        )
        return user

    def test_no_user(self):
        user = User.objects.create(username="test")

        errored = False
        try:
            push_message_service = PushMessageService(user)
        except DeviceMissingError:
            errored = True

        self.assertTrue(errored)

    def test_gets_user_device(self):
        user = self.make_user()

        push_message_service = PushMessageService(user)

        self.assertIsNotNone(push_message_service.device)

    @patch.object(ClientBase, 'send', return_value="example-uuid")
    def test_sends_notification(self, send):
        user = self.make_user()
        push_message_service = PushMessageService(user)

        result = push_message_service.send_notification("Example message")

        self.assertTrue(result)
        message = Message.objects.get(recipient=user)
        self.assertEqual(str(message.uuid), send.call_args[0][0]['messageId'])
        self.assertEqual(message.message_type, Message.NOTIFICATION)

    @patch.object(ClientBase, 'send', return_value="example-uuid")
    def test_sends_data(self, send):
        user = self.make_user()
        push_message_service = PushMessageService(user)

        result = push_message_service.send_data({
            'some': 'data',
            'example': 1234
        })

        self.assertTrue(result)
        message = Message.objects.get(recipient=user)
        self.assertEqual(str(message.uuid), send.call_args[0][0]['messageId'])
        self.assertEqual(message.message_type, Message.DATA)

    @patch.object(ClientBase, 'send', return_value="example-uuid")
    def test_makes_message_receipt(self, send):
        user = self.make_user()
        push_message_service = PushMessageService(user)

        push_message_service.send_notification("Hello World")

        message_receipt = MessageReceipt.objects.get(message__recipient=user)
        self.assertEqual(message_receipt.type, MessageReceipt.SENT)

    def raise_message_failure(self, request):
        raise ClientBase.MessageSendError('Mock error')

    @patch.object(ClientBase, 'send', raise_message_failure)
    def test_handles_message_send_failure(self):
        user = self.make_user()
        push_message_service = PushMessageService(user)

        with self.assertRaises(push_message_service.MessageSendError):
            result = push_message_service.send_notification("Hello World")

class TestFirebaseMessageService(TestCase):

    def make_service(self):
        user = User.objects.create(username="test")
        device = Device.objects.create(
            user = user,
            type = 'android',
            token = 'example-token',
            active = True
        )
        return FirebaseMessageService(device)

    def successful_send(url, headers, json):
        class MockResponse():
            status_code = 200
            def json(self):
                return {
                    'multicast_id': 'example-id',
                    'success': 1,
                    'failure': 0
                }
        return MockResponse()

    @patch.object(requests, 'post', successful_send)
    def test_send(self):
        firebase_message_service = self.make_service()

        message_id = firebase_message_service.send({})

        self.assertEqual(message_id, 'example-id')

    def failed_send(url, headers, json):
        class MockResponse():
            status_code = 200
            def json(self):
                return {
                    'multicast_id': 'meh',
                    'success': 0,
                    'failure': 1
                }
        return MockResponse()

    @patch.object(requests, 'post', failed_send)
    def test_send_fails(self):
        firebase_message_service = self.make_service()

        failed = False
        try:
            firebase_message_service.send({})
        except FirebaseMessageService.MessageSendError:
            failed = True
        
        self.assertTrue(failed)

    def test_format_data(self):
        firebase_message_service = self.make_service()

        formatted_request = firebase_message_service.format_data({})

        self.assertIn('data', formatted_request)
    
    def test_format_notification(self):
        firebase_message_service = self.make_service()

        formatted_request = firebase_message_service.format_notification("Hello World", "Title", {'example': 'data'})

        self.assertIn('data', formatted_request)
        self.assertEqual('Hello World', formatted_request['data']['body'])
        self.assertEqual('Title', formatted_request['data']['title'])
        self.assertEqual('data', formatted_request['data']['example'])
