from datetime import date
from datetime import datetime
import random
import pytz
from unittest.mock import patch

from django.test import TestCase

from days.services import DayService
from push_messages.services import PushMessageService
from walking_suggestion_times.signals import suggestion_times_updated

from .models import Configuration
from .models import DailyTask
from .models import Decision
from .models import SuggestionTime
from .models import User
from .models import WalkingSuggestionSurvey
from .tasks import randomize_walking_suggestion_survey

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


class TestWalkingSuggestionSurveyTask(TestBase):

    def setUp(self):
        super().setUp()

        self.configuration.treatment_probability = 0.2
        self.configuration.save()

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
        current_datetime_patch = patch.object(DayService, 'get_current_datetime')
        self.addCleanup(current_datetime_patch.stop)
        self.current_datetime = current_datetime_patch.start()
        self.current_datetime.return_value = datetime.utcnow()

        current_date_patch = patch.object(DayService, 'get_current_date')
        self.addCleanup(current_date_patch.stop)
        self.current_date = current_date_patch.start()
        self.current_date.return_value = date.today()

        send_notification_patch = patch.object(PushMessageService, 'send_notification')
        self.addCleanup(send_notification_patch.stop)
        send_notification_patch.start()

        random_patch = patch.object(random, 'random')
        self.addCleanup(random_patch.stop)
        self.random = random_patch.start()
        self.random.return_value = 1

    def test_creates_walking_suggestion_survey_decision_lunch(self):
        self.current_date.return_value = date(2020,11,8)
        self.current_datetime.return_value = datetime(2020,11,8,13).astimezone(pytz.UTC)

        randomize_walking_suggestion_survey(username=self.user.username)

        decision = Decision.objects.get(user=self.user)
        self.assertEqual(decision.treatment_probability, self.configuration.treatment_probability)
        self.assertEqual(decision.suggestion_time_category, SuggestionTime.LUNCH)

    def test_creates_walking_suggestion_survey_decision_postdinner(self):
        self.current_date.return_value = date(2020,11,8)
        self.current_datetime.return_value = datetime(2020,11,8,18,45).astimezone(pytz.UTC)

        randomize_walking_suggestion_survey(username=self.user.username)

        decision = Decision.objects.get(user=self.user)
        self.assertEqual(decision.treatment_probability, self.configuration.treatment_probability)
        self.assertEqual(decision.suggestion_time_category, SuggestionTime.POSTDINNER)

    def test_does_not_create_walking_suggestion_survey(self):
        self.current_date.return_value = date(2020,11,8)
        self.current_datetime.return_value = datetime(2020,11,8,6).astimezone(pytz.UTC)

        randomize_walking_suggestion_survey(username=self.user.username)

        self.assertEqual(Decision.objects.filter(user=self.user).count(), 0)

    def test_does_not_make_second_decision_if_already_decision_for_category(self):
        self.current_date.return_value = date(2020,11,8)
        self.current_datetime.return_value = datetime(2020,11,8,18,45).astimezone(pytz.UTC)
        
        randomize_walking_suggestion_survey(username=self.user.username)
        randomize_walking_suggestion_survey(username=self.user.username)

        self.assertEqual(Decision.objects.filter(user=self.user).count(), 1)
