from rest_framework.test import APITestCase
from django.urls import reverse

from unittest.mock import patch
from rest_framework.response import Response

from django.contrib.auth.models import User
from fitbit.api import FitbitOauth2Client

class FitbitAuthorizationTest(APITestCase):

    @patch('fitbit_api.views.login')
    def test_authorize(self, login):
        user = User.objects.create(username="test")

        response = self.client.get(reverse('fitbit-authorize-login', kwargs={
            'username': 'test'
        }))

        login.assert_called()
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('fitbit-authorize-redirect'))

    def mock_access_token(self, code):
        return {
            'access_token': '1234',
            'user_id': 'example-fitbit-id',
            'refresh_token': '789',
            'expires_at': '1234567890'
        }

    @patch.object(FitbitOauth2Client, 'fetch_access_token', mock_access_token)
    @patch('fitbit_api.views.send_notification')
    def test_process(self, send_notification):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user)
        response = self.client.get(reverse('fitbit-authorize-process'), {
            'code': 'sample-code-1234'
        })

        send_notification.assert_called_once()
        args, kwargs = send_notification.call_args
        self.assertEqual(kwargs['data']['fitbit_id'], 'example-fitbit-id')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('fitbit-authorize-complete'))

    def mock_access_token_fail(self, code):
        raise KeyError("Fake error!")

    @patch.object(FitbitOauth2Client, 'fetch_access_token', mock_access_token_fail)
    @patch('fitbit_api.views.send_notification')
    def test_process_fail(self, send_notification):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user)
        response = self.client.get(reverse('fitbit-authorize-process'), {
            'code': 'sample-code-1234'
        })

        send_notification.assert_called_once()
        args, kwargs = send_notification.call_args
        self.assertEqual(kwargs['data']['fitbit_id'], None)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('fitbit-authorize-complete'))        
