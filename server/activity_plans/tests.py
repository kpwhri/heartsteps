import pytz
from datetime import datetime

from rest_framework.test import APITestCase
from django.urls import reverse

from django.contrib.auth.models import User
from activity_logs.models import ActivityType
from activity_plans.models import ActivityPlan

class ActivityPlansListTest(APITestCase):

    def test_create_activity_plan(self):
        user = User.objects.create(username="test")
        ActivityType.objects.create(
            name="swim"
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('activity-plans'), {
            'type': 'swim',
            'start': '2018-09-05T14:45',
            'duration': '30',
            'vigorous': True,
            'complete': False
        })

        self.assertEqual(response.status_code, 201)

    def test_create_custom_activity_type(self):
        pass

    def test_get_user_activity_plans_in_time_range(self):
        user = User.objects.create(username="test")
        walk = ActivityType.objects.create(
            name="walk"
        )
        plan = ActivityPlan.objects.create(
            user = user,
            type = walk,
            start = datetime(2018, 9, 7, tzinfo=pytz.UTC),
            duration = 20
        )
        # Out of range plan that should not show up
        ActivityPlan.objects.create(
            user = user,
            type = walk,
            start = datetime(2018, 10, 7, tzinfo=pytz.UTC),
            duration = 20
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('activity-plans'), {
            'start': '2018-09-05T14:45',
            'end': '2018-09-12T14:45'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(plan.uuid))
