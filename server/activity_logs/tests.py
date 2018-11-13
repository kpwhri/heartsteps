from unittest.mock import patch
from datetime import datetime
import pytz

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from fitbit_api.models import FitbitAccount, FitbitDay

class ActivitySummaryViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.client.force_authenticate(self.user)

        self.account = FitbitAccount.objects.create(
            user = self.user,
            fitbit_user = "test"
        )

    def create_day(self, date):
        FitbitDay.objects.create(
            account = self.account,
            date = date,
            active_minutes = 10,
            total_steps = 10
        )

    def test_get_day(self):
        self.create_day(datetime(2018, 10, 16))

        response = self.client.get(reverse('activity-summary-day', kwargs={
            'day': '2018-10-16'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['date'], '2018-10-16')
        self.assertEqual(response.data['total_steps'], 10)
        self.assertEqual(response.data['active_minutes'], 10)

    def test_get_missing_day(self):
        response = self.client.get(reverse('activity-summary-day', kwargs={
            'day': '2018-10-16'
        }))
        self.assertEqual(response.status_code, 404)


    def test_get_date_range(self):
        self.create_day(datetime(2018, 10, 16))
        self.create_day(datetime(2018, 10, 17))
        self.create_day(datetime(2018, 10, 18))
        self.create_day(datetime(2018, 10, 19))

        response = self.client.get(reverse('activity-summary-date-range', kwargs={
            'start': '2018-10-16',
            'end': '2018-10-18'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[-1]['date'], '2018-10-18')

    def test_date_range_misformatted(self):
        response = self.client.get(reverse('activity-summary-date-range', kwargs={
            'start': '2018/10/16',
            'end': 'misformatted date'
        }))

        self.assertEqual(response.status_code, 400)
