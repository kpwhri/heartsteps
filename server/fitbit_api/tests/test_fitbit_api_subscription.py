from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

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
