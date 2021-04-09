from datetime import date
from datetime import timedelta

from django.test import TestCase

from .models import ActivitySurveyConfiguration
from .models import BurstPeriod
from .models import Configuration
from .models import User
from .models import WalkingSuggestionSurveyConfiguration

class TestBurstPeriodGeneration(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.configuration = Configuration.objects.create(
            user=self.user,
            enabled = True
        )

    def test_does_not_generate_dates_if_disabled(self):
        self.configuration.enabled = False
        self.configuration.save()
        start = date.today()
        end = date.today() + timedelta(days=self.configuration.interval_length)

        self.configuration.generate_schedule(start, end)

        total_burst_periods = BurstPeriod.objects.filter(user=self.user).count()
        self.assertEqual(total_burst_periods, 0)

    def test_generates_single_burst_period(self):
        start = date.today()
        end = date.today() + timedelta(days=self.configuration.interval_length)

        self.configuration.generate_schedule(start, end)

        total_burst_periods = BurstPeriod.objects.filter(user=self.user).count()
        self.assertEqual(total_burst_periods, 1)

    def test_generates_burst_periods(self):
        number_of_periods = 4
        duration = self.configuration.interval_length * number_of_periods
        start = date.today()
        end = date.today() + timedelta(days=duration)

        self.configuration.generate_schedule(start, end)

        periods = BurstPeriod.objects.filter(user = self.user).all()
        self.assertEqual(len(periods), number_of_periods)

class TestUpdatesBurtProbabilityAccordingToSchedule(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.configuration = Configuration.objects.create(
            user=self.user
        )
        ActivitySurveyConfiguration.objects.create(
            user = self.user
        )
        WalkingSuggestionSurveyConfiguration.objects.create(
            user = self.user
        )

    def test_does_not_change_intervention_probability_when_disabled(self):
        self.configuration.enabled = False
        self.configuration.save()
        BurstPeriod.objects.create(
            user = self.user,
            start = date.today(),
            end = date.today()
        )

        self.configuration.update_intervention_configurations(date.today())

        activity_survey_configuration = ActivitySurveyConfiguration.objects.get(user = self.user)
        walking_suggestion_configuration = WalkingSuggestionSurveyConfiguration.objects.get(user = self.user)
        self.assertEqual(activity_survey_configuration.treatment_probability, 1)
        self.assertEqual(walking_suggestion_configuration.treatment_probability, 1)


    def test_sets_burst_probability_when_scheduled(self):
        # Burst period is today, and the day after tomorrow until next week
        BurstPeriod.objects.create(
            user = self.user,
            start = date.today(),
            end = date.today()
        )
        BurstPeriod.objects.create(
            user = self.user,
            start = date.today() + timedelta(days=2),
            end = date.today() + timedelta(days=7)
        )

        self.configuration.update_intervention_configurations(date.today())

        activity_survey_configuration = ActivitySurveyConfiguration.objects.get(user = self.user)
        walking_suggestion_configuration = WalkingSuggestionSurveyConfiguration.objects.get(user = self.user)
        self.assertEqual(activity_survey_configuration.treatment_probability, 1)
        self.assertEqual(walking_suggestion_configuration.treatment_probability, 1)

        self.configuration.update_intervention_configurations(date.today() + timedelta(days=1))

        activity_survey_configuration = ActivitySurveyConfiguration.objects.get(user = self.user)
        walking_suggestion_configuration = WalkingSuggestionSurveyConfiguration.objects.get(user = self.user)
        self.assertEqual(activity_survey_configuration.treatment_probability, 0.2)
        self.assertEqual(walking_suggestion_configuration.treatment_probability, 0)

        self.configuration.update_intervention_configurations(date.today() + timedelta(days=4))

        activity_survey_configuration = ActivitySurveyConfiguration.objects.get(user = self.user)
        walking_suggestion_configuration = WalkingSuggestionSurveyConfiguration.objects.get(user = self.user)
        self.assertEqual(activity_survey_configuration.treatment_probability, 1)
        self.assertEqual(walking_suggestion_configuration.treatment_probability, 1)
