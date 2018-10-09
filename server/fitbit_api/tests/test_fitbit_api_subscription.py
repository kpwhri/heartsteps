from unittest.mock import patch

from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from fitbit_api.models import FitbitSubscription, FitbitAccount
from fitbit_api.services import FitbitClient
from fitbit_api.tasks import subscribe_to_fitbit

class FitbitApiSubscriptionTest(TestCase):

    def make_fitbit_account(self):
        return FitbitAccount.objects.create(
            user = User.objects.create(username="test"),
            fitbit_user = 'fake-user',
            access_token = 'access-token',
            refresh_token = 'refresh-token',
            expires_at = 1234
        )

    @patch.object(FitbitClient, 'subscribe')
    def test_creates_subscription(self, fitbit_client_subscribe):
        fitbit_account = self.make_fitbit_account()

        subscribe_to_fitbit(fitbit_account.user.username)

        fitbit_client_subscribe.assert_called()

class FitbitApiSubscriptionVerify(APITestCase):

    @patch.object(FitbitClient, 'verify_subscription_code', return_value=True)
    def test_responds_to_verify(self, verify_subscription_code):
        response = self.client.get(reverse('fitbit-subscription'), {
            'verify': 'successful-code'
        })
        self.assertEqual(response.status_code, 204)
        verify_subscription_code.assert_called_with('successful-code')

    @patch.object(FitbitClient, 'verify_subscription_code', return_value=False)
    def test_responds_to_incorrect_verify(self, verify_subscription_code):
        response = self.client.get(reverse('fitbit-subscription'), {
            'verify': 'incorrect-code'
        })
        self.assertEqual(response.status_code, 404)
        verify_subscription_code.assert_called_with('incorrect-code')
