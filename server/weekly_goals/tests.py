from unittest.mock import patch
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from .models import WeeklyGoal, Week, User

class WeeklyGoalTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.client.force_authenticate(user=self.user)

        self.week = Week.objects.create(
            user = self.user,
            start_date = timezone.now(),
            end_date = timezone.now() + timedelta(days=3)
        )

    def test_returns_error_if_no_week(self):
        response = self.client.get(reverse('weekly-goal', kwargs={
            'week_id': 'ABCD-1234'
        }))

        self.assertEqual(response.status_code, 404)

    def test_returns_goal_if_exists(self):
        WeeklyGoal.objects.create(
            user = self.user,
            week = self.week,
            minutes = 15,
            confidence = 1
        )

        response = self.client.get(reverse('weekly-goal', kwargs={
            'week_id': self.week.id
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['minutes'], 15)
        self.assertEqual(response.data['confidence'], 1)

    def test_updates_goal(self):
        WeeklyGoal.objects.create(
            user = self.user,
            week = self.week,
            minutes = 10,
            confidence = 0
        )
        
        response = self.client.post(reverse('weekly-goal', kwargs={
            'week_id': self.week.id
        }), {
            'minutes': 75,
            'confidence': 0.75
        })

        self.assertEqual(response.status_code, 200)
        goal = WeeklyGoal.objects.get()
        self.assertEqual(goal.minutes, 75)
        self.assertEqual(goal.confidence, 0.75)
