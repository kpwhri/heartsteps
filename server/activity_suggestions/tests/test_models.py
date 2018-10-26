from django.test import TestCase
from django.contrib.auth.models import User

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from activity_suggestions.models import SuggestionTime

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
