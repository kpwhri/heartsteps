from rest_framework.test import APITestCase
from django.urls import reverse

from django.utils import timezone
from datetime import timedelta

from unittest.mock import patch
from rest_framework.response import Response

from django.contrib.auth.models import User
from fitbit.api import FitbitOauth2Client

from fitbit_api.models import FitbitAccount, FitbitAccountUser
from fitbit_authorize.models import AuthenticationSession

# TODO: remove print debugging
class FitbitAuthorizationTest(APITestCase):

    def test_authorization_start(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user)
        response = self.client.post(reverse('fitbit-authorize-start'))
        # print('fitbit_authorize_start_response:\n', response, '\n')
        # print('Fitbit Objects Count: ', FitbitAccount.objects.count(), '\n')
        self.assertEqual(response.status_code, 201)

        session = AuthenticationSession.objects.get(user=user, token=response.data['token'])
        self.assertIsNotNone(session)

    def test_authorize(self):
        user = User.objects.create(username="test")
        session = AuthenticationSession.objects.create(user=user)

        response = self.client.get(reverse('fitbit-authorize-login', kwargs={
            'token': str(session.token)
        }))
        # print('fitbit_authorize_login_response:\n', response, '\n')
        # print('Fitbit Objects Count: ', FitbitAccount.objects.count(), '\n')

        self.assertEqual(response.status_code, 302)

    def test_authorize_fails(self):
        response = self.client.get(reverse('fitbit-authorize-login', kwargs={
            'token': 'fake-token'
        }))

        # print('test_authorize_fail_response:\n', response, '\n')
        # print('Fitbit Objects Count: ', FitbitAccount.objects.count(), '\n')
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

        # print('test_authorize_invalid_time_response:\n', response, '\n')
        # print('Fitbit Objects Count: ', FitbitAccount.objects.count(), '\n')
        self.assertEqual(response.status_code, 404)

    def test_process_with_no_session(self):
        user = User.objects.create(username="test")

        response = self.client.get(reverse('fitbit-authorize-process'), {
            'code': 'sample-1234',
            'state': 'fake-state'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(0, FitbitAccount.objects.count())

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
        self.assertEqual(0, FitbitAccount.objects.count())

    def mock_access_token(self, code, redirect_uri=None):
        return {
            'access_token': '1234',
            'user_id': 'example-fitbit-id',
            'refresh_token': '789',
            'expires_at': '1234567890'
        }

    # TODO: uncomment test after restoring subcribe_to_fitbit to async
    # @patch.object(FitbitOauth2Client, 'fetch_access_token', mock_access_token)
    # @patch('fitbit_api.tasks.subscribe_to_fitbit.apply_async')
    # def test_process(self, subscribe_to_fitbit):
    #     user = User.objects.create(username="test")
    #     AuthenticationSession.objects.create(
    #         user = user,
    #         state = 'example-state'
    #     )

    #     response = self.client.get(reverse('fitbit-authorize-process'), {
    #         'code': 'sample-1234',
    #         'state': 'example-state'
    #     })

    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, reverse('fitbit-authorize-complete'))
    #     session = AuthenticationSession.objects.get(user=user)
    #     self.assertTrue(session.disabled)
    #     self.assertEqual(1, FitbitAccountUser.objects.filter(user=user).count())
    #     fitbit_account = FitbitAccountUser.objects.get(user=user)
    #     self.assertEqual(fitbit_account.account.fitbit_user, 'example-fitbit-id')
    #     # import pdb; pdb.set_trace()
    #     subscribe_to_fitbit.assert_called()
    #     # print('test_process_response', response, '\n')
    #     # print('Fitbit Objects Count: ', FitbitAccount.objects.count(), '\n')
    #     # print('Fitbit Object Access Token: ', fitbit_account.account.access_token, '\n')


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

        self.assertEqual(0, FitbitAccount.objects.count())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('fitbit-authorize-complete'))

    def test_authorize_saves_redirect(self):
        user = User.objects.create(username="test")
        session = AuthenticationSession.objects.create(user=user)

        response = self.client.get(
            path = reverse('fitbit-authorize-login', kwargs={
                'token': str(session.token)
            }),
            data = {
                'redirect': '/example/redirect'
            }
        )

        session = AuthenticationSession.objects.get(user = user)
        self.assertEqual(session.redirect, '/example/redirect')

    # TODO: uncomment test after restoring subcribe_to_fitbit to async
    # @patch.object(FitbitOauth2Client, 'fetch_access_token', mock_access_token)
    # @patch('fitbit_api.tasks.subscribe_to_fitbit.apply_async')
    # def test_process_redirects(self, subscribe_to_fitbit):
    #     user = User.objects.create(username="test")
    #     AuthenticationSession.objects.create(
    #         user = user,
    #         state = 'example-state',
    #         redirect = '/example/url'
    #     )

    #     response = self.client.get(reverse('fitbit-authorize-process'), {
    #         'code': 'sample-1234',
    #         'state': 'example-state'
    #     })

    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, '/example/url')

    def test_complete(self):
        user = User.objects.create(username="test")

        response = self.client.get(reverse('fitbit-authorize-complete'))

        self.assertEqual(response.status_code, 200)
