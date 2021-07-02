import json
from datetime import datetime, timedelta
from django.urls import reverse
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

