import json
from datetime import datetime, timedelta
from fitbit_clock_face.services import StepCountService
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APITestCase

from .models import ClockFace
from .models import ClockFaceStepCount
from .models import User

class RecordStepCountsView(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.clockface = ClockFace.objects.create(
            user = self.user
        )
        self.request_headers = {
            'HTTP_CLOCK_FACE_PIN': self.clockface.pin,
            'HTTP_CLOCK_FACE_TOKEN': str(self.clockface.token)
        }

    def test_creates_step_counts(self):

        step_counts = []
        base_step_count = 200
        for offset in range(10):
            dt = datetime.now() - timedelta(minutes=5*10) + timedelta(minutes=5*offset)
            step_count = {
                'time': int(dt.timestamp()*1000),
                'steps': base_step_count + 50 * offset
            }
            step_counts.append(step_count)
        response = self.client.post(
            path = reverse('clock-face-step-counts'),
            data = json.dumps({
                'step_counts': step_counts
            }),
            content_type='application/json',
            HTTP_CLOCK_FACE_PIN = self.clockface.pin,
            HTTP_CLOCK_FACE_TOKEN = str(self.clockface.token)
        )

        self.assertEqual(response.status_code, 201)
        step_counts = [step_count for step_count in ClockFaceStepCount.objects.filter(user=self.user).order_by('time')]
        self.assertEqual(len(step_counts), 10)
        self.assertEqual(step_counts[0].steps, 200)

class StepCountServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')

    def test_step_count_service_gets_step_counts(self):
        ClockFaceStepCount.objects.create(
            user = self.user,
            time = timezone.now() - timedelta(minutes=10),
            steps = 150
        )
        ClockFaceStepCount.objects.create(
            user = self.user,
            time = timezone.now() - timedelta(minutes=5),
            steps = 250
        )
        ClockFaceStepCount.objects.create(
            user = self.user,
            time = timezone.now(),
            steps = 350
        )

        service = StepCountService(user=self.user)
        step_count = service.get_step_count_between(
            start = timezone.now()-timedelta(minutes=15),
            end = timezone.now()
        )

        self.assertEqual(step_count, 200)

