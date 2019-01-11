import pytz
from datetime import datetime

from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone

from activity_plans.models import ActivityLog, ActivityPlan, ActivityType, User

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

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.client.force_authenticate(user=self.user)

        self.plan = ActivityPlan.objects.create(
            user = self.user,
            type = ActivityType.objects.create(name="walk"),
            start = timezone.now(),
            duration = 15
        )

    def test_can_not_get_other_activity_plan(self):
        plan = ActivityPlan.objects.create(
            user = User.objects.create(username="other"),
            type = ActivityType.objects.create(name="run"),
            start = timezone.now(),
            duration = 7
        )

        response = self.client.get(reverse('activity-plan-detail', kwargs={
            'plan_id': plan.id
        }))

        self.assertEqual(404, response.status_code)

    def test_get_activity_plan(self):
        response = self.client.get(reverse('activity-plan-detail', kwargs={
            'plan_id': self.plan.id
        }))

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.plan.id, response.data['id'])
        self.assertEqual('walk', response.data['type'])

    def test_update_activity_plan(self):
        ActivityType.objects.create(name="swim")

        response = self.client.post(reverse('activity-plan-detail', kwargs={
            'plan_id': self.plan.id
        }), {
            'type': 'swim',
            'start': '2018-09-05T14:45',
            'duration': 30,
            'vigorous': True,
            'complete': False
        })

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.plan.id, response.data['id'])
        self.assertEqual('swim', response.data['type'])
        self.assertEqual(response.data['start'], '2018-09-05T14:45:00Z')
        self.assertEqual(response.data['duration'], 30)
        self.assertEqual(response.data['vigorous'], True)
        self.assertEqual(response.data['complete'], False)

    def test_complete_plan_creates_log(self):
        response = self.client.post(reverse('activity-plan-detail', kwargs={
            'plan_id': self.plan.id
        }), {
            'type': 'walk',
            'start': timezone.now(),
            'duration': 30,
            'vigorous': True,
            'complete': True
        })

        activity_log = ActivityLog.objects.get()
        activity_plan = ActivityPlan.objects.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['complete'], True)

        self.assertEqual(activity_log.user, self.user)
        self.assertEqual(activity_plan.activity_log.id, activity_log.id)
        self.assertEqual(activity_plan.type, activity_log.type)
        self.assertEqual(activity_plan.vigorous, activity_log.vigorous)
        self.assertEqual(activity_plan.start, activity_log.start)
        self.assertEqual(activity_plan.duration, activity_log.duration)

    def test_uncomplete_plan_destroys_log(self):
        self.plan.update_activity_log()

        self.assertEqual(ActivityLog.objects.count(), 1)

        response = self.client.post(reverse('activity-plan-detail', kwargs={
            'plan_id': self.plan.id
        }), {
            'type': 'walk',
            'start': self.plan.start,
            'duration': 30,
            'vigorous': True,
            'complete': False
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['complete'], False)
        self.assertEqual(ActivityLog.objects.count(), 0)

    def test_delete_activity_plan(self):
        response = self.client.delete(reverse('activity-plan-detail', kwargs={
            'plan_id': self.plan.id
        }))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(ActivityPlan.objects.count(), 0)
