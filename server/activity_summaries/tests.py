from unittest.mock import patch
from datetime import datetime
import pytz
import uuid

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from fitbit_api.models import FitbitAccount, FitbitAccountUser, FitbitDay, User


class ActivitySummaryViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.client.force_authenticate(self.user)

        self.account = FitbitAccount.objects.create(
            fitbit_user = "test"
        )
        FitbitAccountUser.objects.create(
            user = self.user,
            account = self.account
        )

    def create_day(self, date):
        FitbitDay.objects.create(
            account = self.account,
            date = date,
            moderate_minutes = 10,
            vigorous_minutes = 5,
            step_count = 10
        )

    def test_get_day(self):
        self.create_day(datetime(2018, 10, 16))

        response = self.client.get(reverse('activity-summary-day', kwargs={
            'day': '2018-10-16'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['date'], '2018-10-16')
        self.assertEqual(response.data['step_count'], 10)
        self.assertEqual(response.data['moderate_minutes'], 10)
        self.assertEqual(response.data['vigorous_minutes'], 5)
        self.assertEqual(response.data['total_minutes'], 20)

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

        self.assertEqual(response.status_code, 404)
