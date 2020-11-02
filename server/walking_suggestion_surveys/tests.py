from django.test import TestCase

from walking_suggestion_times.signals import suggestion_times_updated

from .models import Configuration
from .models import DailyTask
from .models import SuggestionTime
from .models import User
from .models import WalkingSuggestionSurvey

class TestBase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            username='test'
        )
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )

class TestDailyTaskConfiguration(TestBase):

    def setUp(self):
        super().setUp()

        SuggestionTime.objects.create(
            category = SuggestionTime.LUNCH,
            hour = 12,
            minute = 30,
            user = self.user
        )
        SuggestionTime.objects.create(
            category = SuggestionTime.POSTDINNER,
            hour = 20,
            minute = 0,
            user = self.user
        )

    def test_creates_daily_tasks_for_walking_suggestion_times(self):
        
        self.configuration.update_survey_times()

        daily_tasks = self.configuration.get_daily_tasks()
        self.assertEqual(len(daily_tasks), 2)
        self.assertTrue('wss-'+SuggestionTime.LUNCH in [dt.category for dt in daily_tasks])
        self.assertTrue('wss-'+SuggestionTime.POSTDINNER in [dt.category for dt in daily_tasks])
        index = [dt.category for dt in daily_tasks].index('wss-'+SuggestionTime.LUNCH)
        lunch_task = daily_tasks[index]
        self.assertEqual(lunch_task.hour, 12)
        self.assertEqual(lunch_task.minute, 30)
        self.assertEqual(lunch_task.task.task, 'walking_suggestion_surveys.tasks.randomize_walking_suggestion_survey')

    def test_updates_daily_tasks_with_walking_suggestion_times(self):
        self.configuration.update_survey_times()
        suggestion_time = SuggestionTime.objects.get(
            category = SuggestionTime.LUNCH,
            user = self.user
        )
        suggestion_time.hour = 13
        suggestion_time.minute = 15
        suggestion_time.save()
        SuggestionTime.objects.create(
            category = SuggestionTime.MORNING,
            hour = 8,
            minute = 45,
            user = self.user
        )
        SuggestionTime.objects.filter(
            category = SuggestionTime.POSTDINNER,
            user = self.user
        ).delete()

        self.configuration.update_survey_times()
        daily_tasks = self.configuration.get_daily_tasks()
        self.assertEqual(len(daily_tasks), 2)
        self.assertTrue('wss-'+SuggestionTime.MORNING in [dt.category for dt in daily_tasks])
        self.assertFalse('wss-'+SuggestionTime.POSTDINNER in [dt.category for dt in daily_tasks])
        index = [dt.category for dt in daily_tasks].index('wss-'+SuggestionTime.LUNCH)
        lunch_task = daily_tasks[index]
        self.assertEqual(lunch_task.hour, 13)
        self.assertEqual(lunch_task.minute, 15)

    def test_responds_to_suggestion_times_updated_signal(self):
        self.configuration.update_survey_times()
        suggestion_time = SuggestionTime.objects.get(
            category = SuggestionTime.LUNCH,
            user = self.user
        )
        suggestion_time.hour = 11
        suggestion_time.minute = 45
        suggestion_time.save()

        suggestion_times_updated.send(User, username=self.user.username)

        daily_tasks = self.configuration.get_daily_tasks()
        index = [dt.category for dt in daily_tasks].index('wss-'+SuggestionTime.LUNCH)
        lunch_task = daily_tasks[index]
        self.assertEqual(lunch_task.hour, 11)
        self.assertEqual(lunch_task.minute, 45)