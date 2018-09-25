from rest_framework.test import APITestCase
from django.urls import reverse

from django.utils import timezone
from datetime import timedelta

from unittest.mock import patch
from rest_framework.response import Response

from django.contrib.auth.models import User
from fitbit.api import FitbitOauth2Client

from fitbit_api.models import FitbitAccount, AuthenticationSession

class FitbitAuthorizationTest(APITestCase):

    def test_authorization_start(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user)
        response = self.client.post(reverse('fitbit-authorize-start'))
        
        self.assertEqual(response.status_code, 201)

        session = AuthenticationSession.objects.get(user=user, token=response.data['token'])
        self.assertIsNotNone(session)

    @patch('fitbit_api.views.redirect')
    @patch('fitbit_api.views.login')
    def test_authorize(self, login, redirect):
        redirect.return_value = Response({})
        
        user = User.objects.create(username="test")
        session = AuthenticationSession.objects.create(user=user)

        response = self.client.get(reverse('fitbit-authorize-login', kwargs={
            'token': str(session.token)
        }))

        login.assert_called()
        redirect.assert_called()

    def test_authorize_fails(self):
        response = self.client.get(reverse('fitbit-authorize-login', kwargs={
            'token': 'fake-token'
        }))

        self.assertEqual(response.status_code, 404)
    
    def test_authorize_invalid_time(self):
        user = User.objects.create(username="test")

        session = AuthenticationSession.objects.create(user=user)
        
        old_token_time = timezone.now() - timedelta(hours=5)
        session.created = old_token_time
        session.save()
        
        response = self.client.get(reverse('fitbit-authorize-login', kwargs={
            'token': session.token
        }))

        self.assertEqual(response.status_code, 404)

    def test_process_with_no_session(self):
        user = User.objects.create(username="test")

        response = self.client.get(reverse('fitbit-authorize-process'), {
            'code': 'sample-1234',
            'state': 'fake-state'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(0, FitbitAccount.objects.filter(user=user).count())

    def test_process_with_invalid_session_time(self):
        user = User.objects.create(username="test")

        session = AuthenticationSession.objects.create(user=user)
        
        old_token_time = timezone.now() - timedelta(hours=5)
        session.created = old_token_time

        session.state = 'example-state'
        session.save()

        response = self.client.get(reverse('fitbit-authorize-process'), {
            'code': 'sample-1234',
            'state': session.state
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(0, FitbitAccount.objects.filter(user=user).count())

    def mock_access_token(self, code, redirect_uri=None):
        return {
            'access_token': '1234',
            'user_id': 'example-fitbit-id',
            'refresh_token': '789',
            'expires_at': '1234567890'
        }

    @patch.object(FitbitOauth2Client, 'fetch_access_token', mock_access_token)
    def test_process(self):
        user = User.objects.create(username="test")
        AuthenticationSession.objects.create(
            user = user,
            state = 'example-state'
        )

        response = self.client.get(reverse('fitbit-authorize-process'), {
            'code': 'sample-1234',
            'state': 'example-state'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('fitbit-authorize-complete'))

        session = AuthenticationSession.objects.get(user=user)
        self.assertTrue(session.disabled)

        self.assertEqual(1, FitbitAccount.objects.filter(user=user).count())

        fitbit_account = FitbitAccount.objects.get(user=user)
        self.assertEqual(fitbit_account.fitbit_user, 'example-fitbit-id')

    def mock_access_token_fail(self, code, redirect_uri=None):
        raise KeyError("Fake error!")

    @patch.object(FitbitOauth2Client, 'fetch_access_token', mock_access_token_fail)
    def test_process_fail(self):
        user = User.objects.create(username="test")
        AuthenticationSession.objects.create(
            user = user,
            state = 'example-state'
        )

        response = self.client.get(reverse('fitbit-authorize-process'), {
            'code': 'sample-code-1234',
            'state': 'example-state'
        })

        session = AuthenticationSession.objects.get(user=user)
        self.assertTrue(session.disabled)

        self.assertEqual(0, FitbitAccount.objects.filter(user=user).count())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('fitbit-authorize-complete'))

    def test_complete(self):
        user = User.objects.create(username="test")

        response = self.client.get(reverse('fitbit-authorize-complete'))

        self.assertEqual(response.status_code, 200)   
