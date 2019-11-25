import pytz
from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

from daily_tasks.models import DailyTask
from locations.services import LocationService
from walking_suggestion_times.signals import suggestion_times_updated
from watch_app.signals import step_count_updated

from walking_suggestions.models import Configuration
from walking_suggestions.models import SuggestionTime
from walking_suggestions.tasks import nightly_update


class ConfigurationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='test'
        )

    def test_creates_default_walking_suggestion_times(self):
        
        configuration = Configuration.objects.create(
            user = self.user
        )

        suggestion_times = [(time.category, time.time_formatted) for time in SuggestionTime.objects.filter(user=self.user).all()]
        self.assertEqual(len(suggestion_times), 5)
        suggestion_times_dict = {}
        for category, time in suggestion_times:
            suggestion_times_dict[category] = time
        self.assertEqual(suggestion_times_dict[SuggestionTime.MORNING], '8:30')
        self.assertEqual(suggestion_times_dict[SuggestionTime.LUNCH], '12:15')
        self.assertEqual(suggestion_times_dict[SuggestionTime.MIDAFTERNOON], '15:00')
        self.assertEqual(suggestion_times_dict[SuggestionTime.EVENING], '18:30')
        self.assertEqual(suggestion_times_dict[SuggestionTime.POSTDINNER], '21:00')
    
    def test_creates_walking_suggestion_tasks(self):
        
        configuration = Configuration.objects.create(
            user = self.user
        )

        daily_tasks = DailyTask.objects.filter(
            user = self.user,
            category__in = ['ws-%s' % (suggestion_time.category) for suggestion_time in SuggestionTime.objects.filter(user=self.user).all()]
        )
        self.assertEqual(len(daily_tasks), 5)
        self.assertEqual([False, False, False, False, False], [task.enabled for task in daily_tasks])

    def test_enables_walking_suggestion_tasks(self):
        configuration = Configuration.objects.create(
            user = self.user
        )

        configuration.enabled = True
        configuration.save()

        daily_tasks = DailyTask.objects.filter(
            user = self.user,
            category__in = ['ws-%s' % (suggestion_time.category) for suggestion_time in SuggestionTime.objects.filter(user=self.user).all()]
        )
        self.assertEqual(len(daily_tasks), 5)
        self.assertEqual([True, True, True, True, True], [task.enabled for task in daily_tasks])
