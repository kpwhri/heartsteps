import pytz
from unittest.mock import patch
from datetime import datetime, date

from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone

from days.services import DayService
from locations.services import LocationService
from walking_suggestion_times.models import SuggestionTime

from activity_plans.models import ActivityLog, ActivityPlan, ActivityType, User

class TestBase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            date_joined = datetime(2019,3,1).astimezone(pytz.UTC)
        )
        self.client.force_authenticate(user=self.user)

        SuggestionTime.objects.create(
            user=self.user,
            category = SuggestionTime.MORNING,
            hour = 8,
            minute = 30
        )
        SuggestionTime.objects.create(
            user=self.user,
            category = SuggestionTime.LUNCH,
            hour = 12,
            minute = 15
        )

class ActivityPlanCreateTest(TestBase):

    def test_create_activity_plan(self):
        ActivityType.objects.create(
            name="swim"
        )

        response = self.client.post(reverse('activity-plans'), {
            'type': 'swim',
            'date': '2019-03-03',
            'timeOfDay': SuggestionTime.MORNING,
            'duration': '30',
            'vigorous': True
        })

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data['id'])

        activity_plan = ActivityPlan.objects.get()
        self.assertEqual(activity_plan.start, datetime(2019, 3, 3, 8, 30).astimezone(pytz.UTC))

class ActivityPlanListTest(TestBase):

    def test_get_user_activity_plans_in_time_range(self):
        walk = ActivityType.objects.create(
            name="walk"
        )
        plan = ActivityPlan.objects.create(
            user = self.user,
            type = walk,
            date = date(2018, 9, 10),
            timeOfDay = SuggestionTime.MORNING,
            duration = 20
        )
        # Out of range plan that should not show up
        ActivityPlan.objects.create(
            user = self.user,
            type = walk,
            date = date(2018, 10, 5),
            timeOfDay = SuggestionTime.MORNING,
            duration = 20
        )

        response = self.client.get(reverse('activity-plans'), {
            'start': '2018-09-05T14:45',
            'end': '2018-09-12T14:45'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(plan.uuid))

class ActivityPlanViewTest(TestBase):

    def setUp(self):
        super().setUp()

        self.plan = ActivityPlan.objects.create(
            user = self.user,
            type = ActivityType.objects.create(name="walk"),
            date = date.today(),
            timeOfDay = SuggestionTime.MORNING,
            duration = 15
        )

    def test_can_not_get_other_activity_plan(self):
        other_user = User.objects.create(username="other")
        SuggestionTime.objects.create(
            user = other_user,
            category = SuggestionTime.LUNCH,
            hour = 14,
            minute = 2
        )
        plan = ActivityPlan.objects.create(
            user = other_user,
            type = ActivityType.objects.create(name="run"),
            date = date.today(),
            timeOfDay = SuggestionTime.LUNCH,
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
            'date': '2018-09-05',
            'timeOfDay': SuggestionTime.LUNCH,
            'duration': 30,
            'vigorous': True,
            'complete': False
        })

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.plan.id, response.data['id'])
        self.assertEqual('swim', response.data['type'])
        self.assertEqual(response.data['date'], '2018-09-05')
        self.assertEqual(response.data['timeOfDay'], SuggestionTime.LUNCH)
        self.assertEqual(response.data['duration'], 30)
        self.assertEqual(response.data['vigorous'], True)
        self.assertEqual(response.data['complete'], False)

    @patch.object(DayService, 'get_timezone_at', return_value=pytz.timezone('Etc/GMT+8'))
    def test_complete_plan_creates_log(self, get_timezone_at):

        response = self.client.post(reverse('activity-plan-detail', kwargs={
            'plan_id': self.plan.id
        }), {
            'type': 'walk',
            'date': '2019-03-03',
            'timeOfDay': SuggestionTime.LUNCH,
            'duration': 30,
            'vigorous': True,
            'complete': True
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['complete'], True)

        activity_log = ActivityLog.objects.get()
        activity_plan = ActivityPlan.objects.get()
        self.assertEqual(activity_log.user, self.user)
        self.assertEqual(activity_plan.activity_log.id, activity_log.id)
        self.assertEqual(activity_plan.type, activity_log.type)
        self.assertEqual(activity_plan.vigorous, activity_log.vigorous)
        self.assertEqual(activity_plan.date, activity_log.date)
        self.assertEqual(activity_plan.timeOfDay, activity_log.timeOfDay)
        self.assertEqual(activity_plan.duration, activity_log.duration)

        tz = pytz.timezone('Etc/GMT+8')
        dt = tz.localize(datetime(2019,3,3,12,15))
        self.assertEqual(activity_log.start, dt.astimezone(pytz.UTC))

    def test_uncomplete_plan_destroys_log(self):
        self.plan.activity_log = ActivityLog.objects.create(
            user = self.user,
            type = self.plan.type,
            duration = 30,
            start = timezone.now()
        )
        self.plan.save()

        self.assertEqual(ActivityLog.objects.count(), 1)

        response = self.client.post(reverse('activity-plan-detail', kwargs={
            'plan_id': self.plan.id
        }), {
            'type': 'walk',
            'date': '2019-03-03',
            'timeOfDay': SuggestionTime.LUNCH,
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
