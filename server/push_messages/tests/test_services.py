from unittest.mock import patch
from django.test import TestCase
import requests

from django.contrib.auth.models import User

from push_messages.models import Message, Device, MessageReceipt
from push_messages.services import PushMessageService, ClientBase, FirebaseMessageService, DeviceMissingError
from push_messages.clients import OneSignalClient
from push_messages.tasks import onesignal_get_received

class TestPushMessageService(TestCase):

    def make_user(self):
        user = User.objects.create(username="test")
        Device.objects.create(
            user = user,
            token = 'example-token',
            type = Device.ANDROID,
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

    def test_gets_most_recent_active_device(self):
        user = self.make_user()

        Device.objects.create(
            user = user,
            token = 'newer-device-token',
            type = Device.ANDROID,
            active = True
        )
        Device.objects.create(
            user = user,
            token = 'newer-deactivated-device-token',
            type = Device.ANDROID,
            active = False
        )

        push_message_service = PushMessageService(user)

        self.assertIsNotNone(push_message_service.device)
        self.assertEqual(push_message_service.device.token, 'newer-device-token')

    @patch.object(ClientBase, 'send', return_value="example-uuid")
    def test_sends_notification(self, send):
        user = self.make_user()
        push_message_service = PushMessageService(user)

        result = push_message_service.send_notification("Example message")

        self.assertTrue(result)
        message = Message.objects.get(recipient=user)
        send_kwargs = send.call_args[1]
        self.assertEqual(str(message.uuid), send_kwargs['data']['messageId'])
        self.assertEqual(message.message_type, Message.NOTIFICATION)
        self.assertEqual(message.body, "Example message")
        self.assertEqual(message.title, "HeartSteps")

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
        send_kwargs = send.call_args[1]
        self.assertEqual(str(message.uuid), send_kwargs['data']['messageId'])
        self.assertEqual(message.message_type, Message.DATA)

    @patch.object(ClientBase, 'send', return_value="example-uuid")
    def test_sends_notification_with_collapse_subject(self, send):
        user = self.make_user()
        push_message_service = PushMessageService(user)

        push_message_service.send_notification(
            body = 'This is only a test',
            collapse_subject = 'test-subject'
        )

        message = Message.objects.get(recipient = user)
        self.assertEqual(message.collapse_subject, 'test-subject')
        send_kwargs = send.call_args[1]
        self.assertEqual(send_kwargs['collapse_subject'], 'test-subject')

    @patch.object(ClientBase, 'send', return_value="example-uuid")
    def test_makes_message_receipt(self, send):
        user = self.make_user()
        push_message_service = PushMessageService(user)

        push_message_service.send_notification("Hello World")

        message_receipt = MessageReceipt.objects.get(message__recipient=user)
        self.assertEqual(message_receipt.type, MessageReceipt.SENT)

    def raise_message_failure(self, body, title, collapse_subject, data):
        raise ClientBase.MessageSendError('Mock error')

    @patch.object(ClientBase, 'send', raise_message_failure)
    def test_handles_message_send_failure(self):
        user = self.make_user()
        push_message_service = PushMessageService(user)

        with self.assertRaises(push_message_service.MessageSendError):
            result = push_message_service.send_notification("Hello World")

        self.assertEqual(Message.objects.count(), 0)

class OneSignalClientTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.device = Device.objects.create(
            type="OneSignal",
            token="faketoken",
            user=self.user
        )

        task_patch = patch.object(onesignal_get_received, 'apply_async')
        self.get_received_task = task_patch.start()
        self.addCleanup(task_patch.stop)

        requests_patch = patch.object(requests, 'post')
        self.request_post = requests_patch.start()
        self.addCleanup(requests_patch.stop)

        def make_mock_request(fails=False, errors=None):
            def mock_request(url, headers=None, json=None):
                if fails:
                    _status_code = 400
                else:
                    _status_code = 200
                if errors:
                    _return_json = {'id':'', 'errors': errors}
                else:
                    _return_json = {'id':'example-message-id'}
                class MockResponse:
                    status_code = _status_code

                    def json(self):
                        return _return_json
                return MockResponse()
            return mock_request
        self.set_mock_request = make_mock_request

    def testSend(self):
        self.request_post.side_effect = self.set_mock_request()
        client = OneSignalClient(self.device)
        test_data = {
            'test': True
        }

        message_id = client.send(
            body = 'test body',
            title = 'test title',
            collapse_subject = 'test collapse',
            data = test_data
        )

        self.assertEqual(message_id, 'example-message-id')
        self.get_received_task.assert_called_with(
            countdown = 300,
            kwargs = {'message_id': 'example-message-id'}
        )
        request_json = self.request_post.call_args[1]['json']
        self.assertEqual(request_json['include_player_ids'], [self.device.token])
        self.assertEqual(request_json['contents']['en'], 'test body')
        self.assertEqual(request_json['headings']['en'], 'test title')
        self.assertEqual(request_json['collapse_id'], 'test collapse')
        self.assertEqual(request_json['data'], test_data)

    def testFail(self):
        self.request_post.side_effect = self.set_mock_request(fails=True)
        client = OneSignalClient(self.device)

        try:
            message_id = client.send({
                'body': 'test',
                'title': 'test'
            })
            self.fail('Test should have failed')
        except OneSignalClient.MessageSendError as e:
            pass

    def testErrors(self):
        self.request_post.side_effect = self.set_mock_request(errors=['Mock error'])
        client = OneSignalClient(self.device)

        try:
            message_id = client.send({
                'body': 'test',
                'title': 'test'
            })
            self.fail('Test should have failed')
        except OneSignalClient.MessageSendError as e:
            pass


