from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from push_messages.models import Device

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


    def test_register_multiple_devices(self):
        user = User.objects.create(username = "test")

        Device.objects.create(
            user = user,
            token = 'old-device',
            type = 'ios',
            active = True,
        )

        Device.objects.create(
            user = user,
            token = 'old-device-1',
            type = 'ios',
            active = True,
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('messages-device'), {
            'token': 'new-token',
            'type': 'android'
        })

        self.assertEqual(response.status_code, 201)

        device = Device.objects.get(token='new-token', user=user)
        self.assertTrue(device.active)
        self.assertEqual(device.type, 'android')

        old_device = Device.objects.get(token='old-device', user=user)
        self.assertFalse(old_device.active)

        old_device = Device.objects.get(token='old-device-1', user=user)
        self.assertFalse(old_device.active)
