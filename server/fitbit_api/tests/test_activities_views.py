from unittest.mock import patch
from datetime import datetime
import pytz

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from fitbit_api.models import FitbitAccount, FitbitDay

class FitbitLogsView(APITestCase):

    def test_get_day(self):
        account = FitbitAccount.objects.create(
            fitbit_user = 'test',
            user = User.objects.create(username="test")
        )
        date = datetime(2018, 10, 16)
        FitbitDay.objects.create(
            account = account,
            date = date,
            active_minutes = 17,
            total_steps = 10
        )

        self.client.force_login(account.user)
        response = self.client.get(reverse('fitbit-logs', kwargs={
            'day': '2018-10-16'
        }))
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['date'], '2018-10-16')
        self.assertEqual(response.data['total_steps'], 10)
        self.assertEqual(response.data['active_minutes'], 17)
