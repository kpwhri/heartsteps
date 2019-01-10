import json
import time
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from anti_sedentary.models import AntiSedentaryDecision
from anti_sedentary.tasks import make_decision

from .models import StepCount
from .tasks import start_decision

def make_fitbit_stepcount(steps):
    timestamp = int(time.time())
    return json.dumps({
        'step_number': steps,
        'step_dtm': timestamp
    })


class AntiSedViewTests(APITestCase):

    @patch.object(start_decision, 'apply_async')
    def test_post_data(self, start_decision):
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

        start_decision.assert_called_with(kwargs={
            'step_count_id': StepCount.objects.get().id
        })

class StartDecisionTaskTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
    
    @patch.object(make_decision, 'apply_async')
    def test_starts_decision(self, make_decision):
        step_count = StepCount.objects.create(
            user = self.user,
            step_number = 7,
            step_dtm = timezone.now()
        )

        start_decision(step_count.id)

        decision = AntiSedentaryDecision.objects.get()
        self.assertEqual(decision.user.id, step_count.user.id)
        make_decision.assert_called_with(kwargs={
            'decision_id': str(decision.id)
        })

    @patch.object(make_decision, 'apply_async')
    def test_does_not_start_decision(self, make_decision):
        step_count = StepCount.objects.create(
            user = self.user,
            step_number = 157,
            step_dtm = timezone.now()
        )

        start_decision(step_count.id)

        self.assertEqual(0, AntiSedentaryDecision.objects.count())
        make_decision.assert_not_called()
