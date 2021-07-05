import json
from datetime import datetime, timedelta
from fitbit_clock_face.services import StepCountService
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import ClockFace
from .models import ClockFaceLog
from .models import StepCount
from .models import User
from .tasks import update_step_counts

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

        update_step_counts_patch = patch.object(update_step_counts, 'delay')
        self.addCleanup(update_step_counts_patch.stop)
        self.update_step_counts = update_step_counts_patch.start()

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
        step_counts = [step_count for step_count in ClockFaceLog.objects.filter(user=self.user).order_by('time')]
        self.assertEqual(len(step_counts), 10)
        self.assertEqual(step_counts[0].steps, 200)
        self.update_step_counts.assert_called_with(
            username='test'
        )

class UpdateStepCountTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username = 'test')

    def create_clock_face_log(self, time, steps):
        return ClockFaceLog.objects.create(
            user = self.user,
            time = time,
            steps = steps
        )

    def test_create_step_counts_from_clock_face_logs(self):
        now = timezone.now()
        self.create_clock_face_log(now-timedelta(minutes=10), 100)
        self.create_clock_face_log(now-timedelta(minutes=5), 150)
        self.create_clock_face_log(now, 200)

        update_step_counts(username=self.user.username)

        self.assertEqual(StepCount.objects.filter(user=self.user).count(), 2)
        last_step_count = StepCount.objects.filter(user=self.user).last()
        self.assertEqual(last_step_count.steps, 50)

    def test_does_not_create_step_count_from_single_log(self):
        self.create_clock_face_log(timezone.now(), 200)

        update_step_counts(username=self.user.username)

        self.assertEqual(StepCount.objects.filter(user = self.user).count(), 0)

    def test_does_not_create_step_count_intervals_greater_than_5_minutes(self):
        now = timezone.now()
        # older log that should not be counted
        self.create_clock_face_log(now-timedelta(minutes=20), 100)
        # create single step count for 5 minutes difference
        self.create_clock_face_log(now-timedelta(minutes=5), 150)
        self.create_clock_face_log(now, 200)

        update_step_counts(username=self.user.username)

        step_count_count = StepCount.objects.filter(user=self.user).count()
        self.assertEqual(step_count_count, 1)

    def test_updates_step_counts_from_clock_face_logs(self):
        now = timezone.now()
        self.create_clock_face_log(now - timedelta(minutes=10), 100)
        self.create_clock_face_log(now - timedelta(minutes=5), 150)
        last_log = self.create_clock_face_log(now, 200)
        
        update_step_counts(username=self.user.username)
        last_log.steps = 250
        last_log.save()
        update_step_counts(username=self.user.username)

        number_of_step_counts = StepCount.objects.filter(user=self.user).count()
        self.assertEqual(2, number_of_step_counts)
        last_step_count = StepCount.objects.filter(user=self.user).last()
        self.assertEqual(last_step_count.steps, 100)




class StepCountServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')

    def test_step_count_service_gets_step_counts(self):
        now = timezone.now()
        StepCount.objects.create(
            user = self.user,
            start = now - timedelta(minutes=10),
            end = now - timedelta(minutes=5),
            steps = 100
        )
        StepCount.objects.create(
            user = self.user,
            start = now - timedelta(minutes=5),
            end = now,
            steps = 200
        )

        service = StepCountService(user=self.user)
        step_count = service.get_step_count_between(
            start = timezone.now()-timedelta(minutes=15),
            end = timezone.now()
        )

        self.assertEqual(step_count, 300)

