from unittest.mock import patch
from datetime import datetime, timedelta
import pytz

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from fitbit_api.models import FitbitAccountUpdate
from fitbit_api.models import FitbitSubscription
from fitbit_api.services import FitbitClient
from fitbit_api.tasks import subscribe_to_fitbit
from fitbit_api.signals import update_date

def make_fitbit_account(username='test'):
    user = User.objects.create(username=username)
    account = FitbitAccount.objects.create(
        fitbit_user = 'fake-%s' % (username),
        access_token = 'access-token',
        refresh_token = 'refresh-token',
        expires_at = 1234
    )
    FitbitAccountUser.objects.create(
        user = user,
        account = account
    )
    return account

class FitbitClientTests(TestCase):

    def setUp(self):
        self.account = make_fitbit_account()
        self.client = FitbitClient(account = self.account)

        make_request_patch = patch.object(FitbitClient, 'make_request')
        self.make_request = make_request_patch.start()
        self.addCleanup(make_request_patch.stop)

        timezone_patch = patch.object(FitbitClient, 'get_timezone')
        self.timezone = timezone_patch.start()
        self.timezone.return_value = pytz.UTC
        self.addCleanup(timezone_patch.stop)

    def test_get_devices(self):
        sync_time = timezone.now() - timedelta(minutes=15)
        formatted_sync_time = self.client.format_datetime(sync_time)
        self.make_request.return_value = [
            {
                'batteryLevel': 98, 
                'deviceVersion': 'Versa 2',
                'id': '12345678',
                'lastSyncTime': formatted_sync_time,
                'mac': 'EXAMPLE-MAC-ADDRESS',
                'type': 'SCALE'
                
            }
        ]

        devices = self.client.get_devices()

        self.assertEqual(devices[0]['id'], '12345678')
        self.assertEqual(devices[0]['battery_level'], 98)
        self.assertEqual(devices[0]['device_version'], 'Versa 2')
        self.assertEqual(devices[0]['last_sync_time'], sync_time)
        self.assertEqual(devices[0]['type'], 'SCALE')
        self.assertEqual(devices[0]['mac'], 'EXAMPLE-MAC-ADDRESS')

    def test_get_device_with_errors(self):
        # Fitbit API didn't return MAC address for SCALE in production
        # Only tracking devices with an ID value, all other values are optional
        self.make_request.return_value = [
            {
                'id': '12345678'
            }
        ]

        devices = self.client.get_devices()

        self.assertEqual(devices[0]['id'], '12345678')
        self.assertEqual(devices[0]['battery_level'], None)
        self.assertEqual(devices[0]['device_version'], None)
        self.assertEqual(devices[0]['last_sync_time'], None)
        self.assertEqual(devices[0]['type'], None)
        self.assertEqual(devices[0]['mac'], None)



class FitbitApiSubscriptionTest(TestCase):

    @patch.object(FitbitClient, 'subscriptions_update')
    @patch.object(FitbitClient, 'is_subscribed', return_value=False)
    @patch.object(FitbitClient, 'subscribe', return_value=True)
    def test_creates_subscription(self, subscribe, is_subscribed, subscriptions_update):
        fitbit_account = make_fitbit_account()

        subscribe_to_fitbit(fitbit_account.fitbit_user)

        subscribe.assert_called()

    @patch.object(FitbitClient, 'subscriptions_update')
    @patch.object(FitbitClient, 'is_subscribed', return_value=True)
    @patch.object(FitbitClient, 'subscribe', return_value=True)
    def test_subscription_does_not_create_if_exists(self, subscribe, is_subscribed, subscriptions_update):
        fitbit_account = make_fitbit_account()

        subscribe_to_fitbit(fitbit_account.fitbit_user)

        subscribe.assert_not_called()

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

class SubscriptionUpdate(APITestCase):

    def setUp(self):
        self.patcher = patch.object(update_date, 'send')
        self.update_date = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_subscription_update(self):
        subscription = FitbitSubscription.objects.create(
            fitbit_account = make_fitbit_account()
        )
        
        response = self.client.post(reverse('fitbit-subscription'), [{
            'ownerId': subscription.fitbit_account.fitbit_user,
            'subscriptionId': str(subscription.uuid),
            'date': '2018-08-17'
        }], format="json")

        self.assertEqual(response.status_code, 204)
        updates = FitbitAccountUpdate.objects.all()
        self.assertEqual(len(updates), 1)
        self.update_date.assert_called_with(
            sender = FitbitAccount,
            fitbit_user = subscription.fitbit_account.fitbit_user,
            date = '2018-08-17'
        )

    def test_subscription_updates_with_multiple_subscriptions(self):
        subscription = FitbitSubscription.objects.create(
            fitbit_account = make_fitbit_account()
        )
        other_subscription = FitbitSubscription.objects.create(
            fitbit_account = make_fitbit_account('other_account')
        )

        response = self.client.post(reverse('fitbit-subscription'), [
            {
                'ownerId': subscription.fitbit_account.fitbit_user,
                'subscriptionId': str(subscription.uuid),
                'date': '2018-09-18'
            }, {
                'ownerId': subscription.fitbit_account.fitbit_user,
                'subscriptionId': str(subscription.uuid),
                'date': '2018-09-20'
            }, {
                'ownerId': other_subscription.fitbit_account.fitbit_user,
                'subscriptionId': str(other_subscription.uuid),
                'date': '2018-09-20'
            }
        ], format="json")

        self.assertEqual(response.status_code, 204)
        updates = FitbitAccountUpdate.objects.all()
        self.assertEqual(len(updates), 3)
        self.assertEqual(self.update_date.call_count, 3)
        self.update_date.assert_any_call(
            sender = FitbitAccount,
            fitbit_user = subscription.fitbit_account.fitbit_user,
            date = '2018-09-18'
        )
        self.update_date.assert_any_call(
            sender = FitbitAccount,
            fitbit_user = subscription.fitbit_account.fitbit_user,
            date = '2018-09-20'
        )
        self.update_date.assert_any_call(
            sender = FitbitAccount,
            fitbit_user = other_subscription.fitbit_account.fitbit_user,
            date = '2018-09-20'
        )
