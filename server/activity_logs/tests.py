from unittest.mock import patch
from datetime import datetime
import pytz
import uuid

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from fitbit_api.models import FitbitAccount, FitbitAccountUser, FitbitDay

from activity_logs.models import User, ActivityLog, ActivityType


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

class ActivityLogsViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create()
        self.client.force_authenticate(self.user)

        ActivityType.objects.create(
            name="run",
            title="Run"
        )
        ActivityType.objects.create(
            name="swim",
            title="Run"
        )

    def create_activity_log(self):
        activity_log = ActivityLog.objects.create(
            user = self.user,
            type = ActivityType.objects.get(name="run"),
            start = timezone.now(),
            duration = 12
        )
        return activity_log

    def test_get_activity_log(self):
        activity_log = self.create_activity_log()

        response = self.client.get(reverse('activity-logs-detail', kwargs={
            'log_id': activity_log.id
        }))

        self.assertEqual(200, response.status_code)

    def test_create_activity_log(self):
        response = self.client.post(reverse('activity-logs-list'), {
            'type': 'run',
            'vigorous': True,
            'start': timezone.now(),
            'duration': 12,
        })

        self.assertEqual(201, response.status_code)
        
        activity_log = ActivityLog.objects.get()
        self.assertEqual(response.data['id'], activity_log.id)

    def test_update_activity_log(self):
        activity_log = self.create_activity_log()

        response = self.client.post(reverse('activity-logs-detail', kwargs={
            'log_id':activity_log.id
        }), {
            'type':'swim',
            'vigorous': True,
            'start': datetime(2018, 12, 18, 10, 15),
            'duration': 20
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], activity_log.id)
        self.assertEqual(response.data['type'], 'swim')
        self.assertEqual(response.data['start'], '2018-12-18T10:15:00Z')

        activity_log = ActivityLog.objects.get()
        self.assertEqual(activity_log.vigorous, True)

    def test_delete_activity_log(self):
        activity_log = self.create_activity_log()

        response = self.client.delete(reverse('activity-logs-detail', kwargs={
            'log_id': activity_log.id
        }))

        self.assertEqual(204, response.status_code)
        self.assertEqual(ActivityLog.objects.count(), 0)
