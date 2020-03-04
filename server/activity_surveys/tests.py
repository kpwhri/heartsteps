from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from fitbit_activities.models import FitbitActivity
from fitbit_activities.models import FitbitActivityType
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser

from .models import Configuration
from .models import ActivitySurvey
from .models import User
from .tasks import randomize_activity_survey

class TestBase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            username='test'
        )
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )
        self.account = FitbitAccount.objects.create(
            fitbit_user = 'test'
        )
        FitbitAccountUser.objects.create(
            account = self.account,
            user = self.user
        )

    def create_fitbit_activity(self):
        activity_type, _ = FitbitActivityType.objects.get_or_create(
            fitbit_id = 123,
            name = 'test'
        )
        activity = FitbitActivity.objects.create(
            account = self.account,
            fitbit_id = 'test-activity',
            type = activity_type,
            start_time = timezone.now() - timedelta(minutes=20),
            end_time = timezone.now() - timedelta(minutes = 5)
        )
        return activity

class ActivitySurveyRandomizationTests(TestBase):

    def setUp(self):
        super().setUp()

        randomize_activity_survey_patch = patch.object(randomize_activity_survey, 'apply_async')
        self.addCleanup(randomize_activity_survey_patch.stop)
        self.randomize_activity_survey = randomize_activity_survey_patch.start()

    def test_randomize_called_when_fitbit_activity_created(self):

        fitbit_activity = self.create_fitbit_activity()

        self.randomize_activity_survey.assert_called_with(
            kwargs = {
                'fitbit_activity_id': fitbit_activity.id,
                'username': 'test'
            }
        )

    def test_does_not_randomize_when_fitbit_activity_updated(self):
        fitbit_activity = self.create_fitbit_activity()
        self.assertEqual(self.randomize_activity_survey.call_count, 1)

        # Making any change....
        fitbit_activity.average_heart_rate = 10
        fitbit_activity.save()

        self.assertEqual(self.randomize_activity_survey.call_count, 1)

    def test_randomizes_survey_for_multiple_accounts(self):
        other_user = User.objects.create(username='other')
        Configuration.objects.create(
            user = other_user,
            enabled = True
        )
        FitbitAccountUser.objects.create(
            account = self.account,
            user = other_user
        )

        self.create_fitbit_activity()

        usernames_called = [call[1]['kwargs']['username'] for call in self.randomize_activity_survey.call_args_list]
        self.assertEqual(len(usernames_called), 2)
        self.assertTrue('test' in usernames_called)
        self.assertTrue('other' in usernames_called)

    def test_does_not_randomize_if_configuration_missing(self):
        self.configuration.delete()

        self.create_fitbit_activity()

        self.randomize_activity_survey.assert_not_called()

    def test_does_not_randomize_if_configuration_missing(self):
        self.configuration.enabled = False
        self.configuration.save()

        self.create_fitbit_activity()

        self.randomize_activity_survey.assert_not_called()
