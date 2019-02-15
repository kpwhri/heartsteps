import json
import time
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from anti_sedentary.tasks import start_decision

from .models import StepCount

def make_fitbit_stepcount(steps):
    timestamp = int(time.time())
    return json.dumps({
        'step_number': steps,
        'step_dtm': timestamp
    })


class AntiSedViewTests(APITestCase):

    def setUp(self):
        start_decision_mock = patch.object(start_decision, 'apply_async')
        start_decision_mock.start()
        self.addCleanup(start_decision_mock.stop)

    def testPost(self):
        user = User.objects.create(username="test")
        self.client.force_authenticate(user=user)

        steps = 10

        response = self.client.post(reverse('anti-sed-steps'),
            make_fitbit_stepcount(steps),
            content_type='application/json'
        )

        response_object = StepCount.objects.get(user=user)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(StepCount.objects.filter(user=user).count(), 1)
        self.assertEqual(response_object.step_number, steps)
