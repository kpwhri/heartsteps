from unittest.mock import patch
from datetime import datetime, date
import pytz
import uuid

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from .models import Day, User

class ActivitySummaryViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username = "test",
            date_joined = datetime(2018, 9, 9, 9, 9).astimezone(pytz.utc) 
        )
        self.client.force_authenticate(self.user)

    def create_day(self, date):
        Day.objects.create(
            user = self.user,
            date = date,
            moderate_minutes = 10,
            vigorous_minutes = 5,
            steps = 10,
            miles = 0.25
        )

    def test_get_invalid_date(self):
        response = self.client.get(reverse('activity-summary-day', kwargs={
            'day': '2018-9-6'
        }))

        self.assertEqual(response.status_code, 404)

    def test_get_default_date(self):
        response = self.client.get(reverse('activity-summary-day', kwargs={
            'day': '2018-12-10'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['steps'], 0)
        self.assertEqual(response.data['miles'], 0)
        self.assertEqual(response.data['minutes'], 0)
        self.assertEqual(response.data['moderateMinutes'], 0)
        self.assertEqual(response.data['vigorousMinutes'], 0)

    def test_get_day(self):
        self.create_day(date(2018, 10, 16))

        response = self.client.get(reverse('activity-summary-day', kwargs={
            'day': '2018-10-16'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['date'], '2018-10-16')
        self.assertEqual(response.data['steps'], 10)
        self.assertEqual(response.data['miles'], 0.25)
        self.assertEqual(response.data['moderateMinutes'], 10)
        self.assertEqual(response.data['vigorousMinutes'], 5)
        self.assertEqual(response.data['minutes'], 20)


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
