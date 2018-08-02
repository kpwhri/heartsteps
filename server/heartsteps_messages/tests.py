from django.urls import reverse

from .models import Message, Device
from django.contrib.auth.models import User

from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APITestCase

class DeviceModelTests(TestCase):

    def make_device(self):
        return Device.objects.create(
            user = User.objects.create(username='test'),
            token = 'example-token',
            type = 'web',
            active = True
        )

    @patch('requests.post')
    def test_send_notification(self, request_post):
        device = self.make_device()

        device.send_notification('Example Title', 'Example Body')

        request_post.assert_called()

    @patch('requests.post')
    def test_send_data(self, request_post):
        device = self.make_device()

        device.send_data({'some': 'data'})

        request_post.assert_called()

class MessageDeviceViewTests(APITestCase):
    def test_get_device(self):
        user = User.objects.create(username="test")

        Device.objects.create(
            user = user,
            token = 'example-token',
            type = 'android',
            active = True
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('messages-device'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['token'], 'example-token')

    def test_get_no_devices_active(self):
        user = User.objects.create(username="test")

        Device.objects.create(
            user = user,
            token = 'example-token',
            type = 'android',
            active = False
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('messages-device'))

        self.assertEqual(response.status_code, 404)


    def test_register_device(self):
        """
        Takes new device registration for a user and saves it
        """
        user = User.objects.create(username = "test")

        Device.objects.create(
            user = user,
            token = 'old-device',
            type = 'ios',
            active = True,
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('messages-device'), {
            'token': 'example-token',
            'type': 'web'
        })

        self.assertEqual(response.status_code, 201)

        device = Device.objects.get(token='example-token', user=user)
        self.assertTrue(device.active)
        self.assertEqual(device.type, 'web')

        old_device = Device.objects.get(token='old-device', user=user)
        self.assertFalse(old_device.active)

class MessageRecievedTests(APITestCase):
    
    def test_marks_recieved(self):
        """
        Returns an authorization token and participant's heartsteps_id when a
        valid enrollment token is passed
        """
        user = User.objects.create(username="test")
        message = Message.objects.create(
            reciepent = user
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('messages-recieved'), {
            'messageId': message.id
        })
        
        self.assertEqual(response.status_code, 201)
