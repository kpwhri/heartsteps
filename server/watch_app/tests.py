import json
import time
from unittest.mock import patch
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from participants.models import Participant, User

from .models import StepCount, WatchInstall
from .signals import step_count_updated

class StepsViewTests(APITestCase):

    def setUp(self):
        user = User.objects.create(username="test")
        self.client.force_authenticate(user=user)

        step_count_updated_patch = patch.object(step_count_updated, 'send')
        self.step_count_updated = step_count_updated_patch.start()
        self.addCleanup(step_count_updated_patch.stop)

    def makeStepCounts(self):
        return [
            {'time': 1556063381849, 'steps': 666}, # ps first entry is ignored
            {'time': 1556063682047, 'steps': 10},
            {'time': 1556063982145, 'steps': 20},
            {'time': 1556064282368, 'steps': 30},
            {'time': 1556064582466, 'steps': 40},
            {'time': 1556064882564, 'steps': 50},
            {'time': 1556065182762, 'steps': 60},
            {'time': 1556065482860, 'steps': 70}
        ]

    def testPost(self):
        request_data = json.dumps({
            'step_number': self.makeStepCounts()
        })
        response = self.client.post(reverse('watch-app-steps'),
            request_data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(StepCount.objects.count(), 7)
        step_count = StepCount.objects.last()
        self.assertEqual(step_count.steps, 70)

        total_steps = 0
        for step_count in StepCount.objects.all():
            total_steps += step_count.steps
        self.assertEqual(total_steps, 280)

        self.step_count_updated.assert_called()

    def testPostUpdatesStepCounts(self):
        request_data = json.dumps({
            'step_number': self.makeStepCounts()
        })
        response = self.client.post(reverse('watch-app-steps'),
            request_data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(StepCount.objects.count(), 7)

        step_counts = [{'time':step_count['time'], 'steps': step_count['steps'] + 10} for step_count in self.makeStepCounts()]
        request_data = json.dumps({
            'step_number': step_counts
        })
        response = self.client.post(reverse('watch-app-steps'),
            request_data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(StepCount.objects.count(), 7)
        step_count = StepCount.objects.last()
        self.assertEqual(step_count.steps, 80)
        total_steps = 0
        for step_count in StepCount.objects.all():
            total_steps += step_count.steps
        self.assertEqual(total_steps, 350)

class LoginViewTests(APITestCase):

    def testLogin(self):
        participant = Participant.objects.create(
            heartsteps_id = "test",
            enrollment_token = "test",
            birth_year = 2019,
            user = User.objects.create(username="test")
        )

        response = self.client.post(
            reverse('watch-app-login'),
            json.dumps({
                "enrollmentToken": "test",
                "birthYear": 2019
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['heartstepsId'], "test")

        install = WatchInstall.objects.get()
        self.assertEqual(install.user.username, "test")

class StatusViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.client.force_authenticate(user=self.user)


    def test_get_status_not_installed(self):

        response = self.client.get(
            reverse('watch-app-status')
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['installed'], None)
        self.assertEqual(response.data['lastUpdated'], None)


    def test_get_status_installed_no_step_counts(self):
        install = WatchInstall.objects.create(
            user = self.user
        )

        response = self.client.get(
            reverse('watch-app-status')
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['installed'], install.updated.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
        self.assertEqual(response.data['lastUpdated'], None)

    def test_get_status_installed_with_step_counts(self):
        install = WatchInstall.objects.create(
            user = self.user
        )

        StepCount.objects.create(
            user = self.user,
            steps = 100,
            start = timezone.now() - timedelta(minutes=15),
            end = timezone.now() - timedelta(minutes=10)
        )
        step_count = StepCount.objects.create(
            user = self.user,
            steps = 12,
            start = timezone.now() - timedelta(minutes=10),
            end = timezone.now() - timedelta(minutes=5)
        )

        response = self.client.get(
            reverse('watch-app-status')
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['installed'], install.updated.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
        self.assertEqual(response.data['lastUpdated'], step_count.end.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
