from django.test import TestCase
from django.urls import reverse

from unittest.mock import patch
from django.test import TestCase, override_settings

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

from django.contrib.auth.models import User
from activity_suggestions.models import SuggestionTime
from heartsteps_randomization.models import Decision
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from activity_suggestions.tasks import start_decision

class SuggestionTimeTestCase(TestCase):

    def test_suggestion_time_creates_periodic_task(self):
        task = SuggestionTime.objects.create(
            user = User.objects.create(username="test"),
            type = 'lunch',
            hour = 15,
            minute = 30
        )

        self.assertIsNotNone(task.scheduled_task)

    def test_removes_periodic_task_when_deleted(self):
        task = SuggestionTime.objects.create(
            user = User.objects.create(username="test"),
            type = 'lunch',
            hour = 15,
            minute = 30
        )
        schedules = CrontabSchedule.objects.all()
        periodic_tasks = PeriodicTask.objects.all()
        
        self.assertEqual(len(periodic_tasks), 1)
        self.assertEqual(len(schedules), 1)

        task.delete()

        periodic_tasks = PeriodicTask.objects.all()
        schedules = CrontabSchedule.objects.all()

        self.assertEqual(len(periodic_tasks), 0)
        self.assertEqual(len(schedules), 0)

class SuggestionTimeUpdateView(APITestCase):

    def test_remove_existing_times_for_user(self):
        user = User.objects.create(username="test")
        SuggestionTime.objects.create(
            user = user,
            type = 'lunch',
            hour = 15,
            minute = 30
        )
        SuggestionTime.objects.create(
            user = user,
            type = 'evening',
            hour = 20,
            minute = 00
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse('activity_suggestions-times'),
            { 'times': [] },
            format='json'
        )

        times = SuggestionTime.objects.filter(user=user)
        
        self.assertEqual(len(times), 0)

    def test_create_times(self):
        user = User.objects.create(username="test")

        times = [
            { 'type': 'morning', 'hour': '7', 'minute': '0', 'timezone': 'US/Pacific' },
            { 'type': 'midafternoon', 'hour': '15', 'minute': '45', 'timezone': 'US/Pacific' }
        ]
        
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse('activity_suggestions-times'),
            { 'times': times },
            format='json'
        )
        

        times = SuggestionTime.objects.filter(user=user).all()
        self.assertEqual(len(times), 2)

        afternoon_time = SuggestionTime.objects.get(user=user, type='midafternoon')
        self.assertEqual(afternoon_time.hour, 15)
        self.assertEqual(afternoon_time.minute, 45)

class TaskTests(TestCase):

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('heartsteps_randomization.tasks.make_decision.delay')
    def test_start_decision(self, make_decision):
        user = User.objects.create(username="test")

        start_decision(user.username, 'evening')

        decision = Decision.objects.get(user=user)

        self.assertEqual(decision.tags.first().tag, 'evening')
        make_decision.assert_called()

