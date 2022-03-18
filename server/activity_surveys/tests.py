from datetime import timedelta
import random
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from fitbit_activities.models import FitbitActivity
from fitbit_activities.models import FitbitActivityType
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from push_messages.models import Device, Message as PushMessage
from push_messages.services import PushMessageService

from .models import Configuration
from .models import Decision
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
        FitbitAccountUser.create_or_update(
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
        FitbitAccountUser.create_or_update(
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

class RandomizeSurveyForFitbitActivityTests(TestBase):

    def setUp(self):
        super().setUp()

        device = Device.objects.create(
            user = self.user,
            token = '12345',
            type = Device.ONESIGNAL,
            active = True
        )

        send_notification_patch = patch.object(PushMessageService, 'send_notification')
        self.addCleanup(send_notification_patch.stop)
        self.send_notification = send_notification_patch.start()
        self.send_notification.return_value = PushMessage.objects.create(
            message_type = PushMessage.NOTIFICATION,
            recipient = self.user,
            device = device
        )

        randomize_patch = patch.object(random, 'random')
        self.addCleanup(randomize_patch.stop)
        self.random = randomize_patch.start()
        self.random.return_value = 0

    def test_creates_survey_for_fitbit_activity(self):
        fitbit_activity = self.create_fitbit_activity()

        randomize_activity_survey(
            fitbit_activity_id = fitbit_activity.id,
            username = 'test'
        )

        decision = Decision.objects.get()
        self.assertEqual(decision.user.username, 'test')
        self.assertTrue(decision.treated)
        self.assertEqual(decision.fitbit_activity.id, fitbit_activity.id)
        self.assertIsNotNone(decision.activity_survey)

    def test_does_not_create_second_survey(self):
        fitbit_activity = self.create_fitbit_activity()

        randomize_activity_survey(
            fitbit_activity_id = fitbit_activity.id,
            username = 'test'
        )
        randomize_activity_survey(
            fitbit_activity_id = fitbit_activity.id,
            username = 'test'
        )

        activity_surveys = ActivitySurvey.objects.filter(
            fitbit_activity=fitbit_activity
        ).count()
        self.assertEqual(activity_surveys, 1)

    def test_does_not_create_survey_if_configuration_disabled(self):
        self.configuration.enabled = False
        self.configuration.save()
        fitbit_activity = self.create_fitbit_activity()

        randomize_activity_survey(
            fitbit_activity_id = fitbit_activity.id,
            username = 'test'
        )

        self.assertEqual(ActivitySurvey.objects.count(), 0)
        decision = Decision.objects.get(user = self.user)
        self.assertFalse(decision.treated)
        self.assertEqual(decision.treatment_probability, 0)

    def test_sends_message_with_survey_to_participant(self):
        fitbit_activity = self.create_fitbit_activity()        

        randomize_activity_survey(
            fitbit_activity_id = fitbit_activity.id,
            username = 'test'
        )

        self.send_notification.assert_called()
        data = self.send_notification.call_args[1]['data']
        survey = ActivitySurvey.objects.get()
        self.assertEqual(data['survey']['id'], str(survey.uuid))


    def test_does_not_send_message_if_activity_ended_more_than_an_hour_ago(self):
        fitbit_activity = self.create_fitbit_activity()
        fitbit_activity.start_time = timezone.now() - timedelta(minutes=120)
        fitbit_activity.end_time = timezone.now() - timedelta(minutes=90)
        fitbit_activity.save()    

        randomize_activity_survey(
            fitbit_activity_id = fitbit_activity.id,
            username = 'test'
        )

        self.send_notification.assert_not_called()
        decision = Decision.objects.get(user = self.user)
        self.assertFalse(decision.treated)
        self.assertEqual(decision.treatment_probability, 0)

    def test_does_not_create_survey_if_not_randomized(self):
        self.random.return_value = 1
        fitbit_activity = self.create_fitbit_activity()

        randomize_activity_survey(
            fitbit_activity_id = fitbit_activity.id,
            username = 'test'
        )

        self.send_notification.assert_not_called()
        
