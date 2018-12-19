from django.test import TestCase

from morning_messages.models import Configuration, DailyTask, User

class MorningMessageTaskTest(TestCase):

    def test_daily_task_created_when_morning_message_created(self):

        configuration = Configuration.objects.create(
            user = User.objects.create(username="test"),
        )

        self.assertIsNotNone(configuration.daily_task)
        self.assertTrue(configuration.daily_task.enabled)

    def test_daily_task_can_be_disabled(self):
        configuration = Configuration.objects.create(
            user = User.objects.create(username="test")
        )

        self.assertTrue(configuration.daily_task.enabled)

        configuration.enabled = False
        configuration.save()

        self.assertFalse(configuration.daily_task.enabled)

    def test_daily_task_destroyed_with_configuration(self):
        configuration = Configuration.objects.create(
            user = User.objects.create(username="test")
        )

        self.assertIsNotNone(configuration.daily_task)

        configuration.delete()

        self.assertEqual(0, DailyTask.objects.count())
