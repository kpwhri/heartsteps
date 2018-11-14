import json
import time

from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase

from anti_seds.models import StepCount


def make_fitbit_stepcount(steps):
    timestamp = int(time.time())
    return json.dumps({
        'step_number': steps,
        'step_dtm': timestamp
    })


class AntiSedTests(APITestCase):

    def test_post_data(self):
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
