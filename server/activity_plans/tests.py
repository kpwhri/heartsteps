import pytz
from datetime import datetime

from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone

from activity_plans.models import ActivityPlan, ActivityType, User

class ActivityPlanCreateTest(APITestCase):

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
        self.assertIsNotNone(response.data['id'])

class ActivityPlanListTest(APITestCase):

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

class ActivityPlanViewTest(APITestCase):

    def test_update_activity_plan(self):
        plan = ActivityPlan.objects.create(
            user = User.objects.create(username="test"),
            type = ActivityType.objects.create(name="walk"),
            start = timezone.now(),
            duration = 15
        )

        self.client.force_authenticate(user=plan.user)
        response = self.client.post(reverse('activity-plan-detail', kwargs={
            'plan_id': plan.id
        }), {
            'type': 'walk',
            'start': '2018-09-05T14:45',
            'duration': '30',
            'vigorous': True,
            'complete': False
        })

        self.assertEqual(response.status_code, 200)    

    def test_delete_activity_plan(self):
        plan = ActivityPlan.objects.create(
            user = User.objects.create(username="test"),
            type = ActivityType.objects.create(name="walk"),
            start = timezone.now(),
            duration = 15
        )

        self.client.force_authenticate(user=plan.user)
        response = self.client.delete(reverse('activity-plan-detail', kwargs={
            'plan_id': plan.id
        }))

        self.assertEqual(response.status_code, 204)
