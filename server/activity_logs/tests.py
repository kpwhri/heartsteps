from unittest.mock import patch
from datetime import datetime
import pytz
import uuid

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from activity_logs.models import User, ActivityLog, ActivityType

class ActivityLogsViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create()
        self.client.force_authenticate(self.user)

        ActivityType.objects.create(name="run")
        ActivityType.objects.create(name="swim")

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
