from unittest.mock import patch
from datetime import date, datetime
import pytz

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase

from push_messages.services import PushMessageService, Device, Message

from morning_messages.models import Configuration, DailyTask, MorningMessage, MorningMessageDecision, MorningMessageSurvey, MorningMessageQuestion, MorningMessageTemplate, User
from morning_messages.services import MorningMessageService, MorningMessageDecisionService
from morning_messages.tasks import send_morning_message

class MorningMessageTestBase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.configuration = Configuration.objects.create(user=self.user)

        Device.objects.create(
            user = self.user,
            active = True
        )
        patch_send_notification = patch.object(PushMessageService, 'send_notification')
        self.send_notification = patch_send_notification.start()
        self.send_notification.return_value = Message.objects.create(
            recipient = self.user,
            content = "foo"
        )
        self.addCleanup(patch_send_notification.stop)

        MorningMessageTemplate.objects.create(
            body = 'Example morning message',
            anchor_message = 'Anchor message'
        )

class MorningMessageConfigurationTest(MorningMessageTestBase):

    def test_daily_task_created_when_morning_message_created(self):
        self.assertIsNotNone(self.configuration.daily_task)
        self.assertTrue(self.configuration.daily_task.enabled)

    def test_daily_task_can_be_disabled(self):
        self.assertTrue(self.configuration.daily_task.enabled)

        self.configuration.enabled = False
        self.configuration.save()

        self.assertFalse(self.configuration.daily_task.enabled)

    def test_daily_task_destroyed_with_configuration(self):
        self.assertIsNotNone(self.configuration.daily_task)

        self.configuration.delete()

        self.assertEqual(0, DailyTask.objects.count())

class MorningMessageServiceTest(MorningMessageTestBase):

    def setUp(self):
        super().setUp()
        self.morning_message_service = MorningMessageService(
            configuration = self.configuration
        )
        self.morning_message_service.create(date(2019, 1, 15))

    def test_get_morning_message(self):
        morning_message = self.morning_message_service.get(date(2019, 1, 15))

        self.assertEqual(morning_message.user, self.user)
        self.assertEqual(morning_message.date, date(2019, 1, 15))

    def test_get_morning_message_does_not_exist(self):
        try:
            morning_message = self.morning_message_service.get(date(2019, 1, 16))
        except MorningMessageService.MessageDoesNotExist:
            morning_message = False
        self.assertFalse(morning_message)

    def test_create_morning_message(self):
        morning_message = self.morning_message_service.create(date(2019, 1, 16))

        self.assertEqual(morning_message.user, self.user)
        self.assertEqual(morning_message.date, date(2019, 1, 16))
        self.assertIsNotNone(morning_message.message_decision)
        self.assertTrue(morning_message.message_decision.treated)
        self.assertEqual(morning_message.message_decision.treatment_probability, 1)

    def test_morning_message_log_matches_morning_message_decision(self):
        self.morning_message_service.update_message(date(2019, 1, 15), None)

        morning_message = self.morning_message_service.get(date(2019, 1 , 15))
        self.assertEqual(morning_message.notification, 'Good Morning')
        self.assertIsNone(morning_message.text)
        self.assertIsNone(morning_message.anchor)

        MorningMessageTemplate.objects.create(
            body = "Example morning message",
            anchor_message = "Anchor message"
        )

        self.morning_message_service.update_message(date(2019, 1, 15), MorningMessageDecision.FRAME_GAIN_ACTIVE)
        
        morning_message = self.morning_message_service.get(date(2019, 1 , 15))
        self.assertEqual(morning_message.notification, 'Example morning message')
        self.assertEqual(morning_message.text, 'Example morning message')
        self.assertEqual(morning_message.anchor, 'Anchor message')

    def test_send_morning_message_default(self):

        self.morning_message_service.send_notification()

        self.send_notification.assert_called()

        morning_message = self.morning_message_service.get(date.today())
        notification = morning_message.get_notification()
        self.assertEqual(notification.recipient, self.user)



class MorningMessageTaskTest(MorningMessageTestBase):

    def test_creates_morning_message(self):
        send_morning_message(username="test")

        self.send_notification.assert_called()
        
        morning_message = MorningMessage.objects.get()
        self.assertEqual(morning_message.user, self.user)
        self.assertEqual(morning_message.date, date.today())

    def test_disabled_task_state(self):
        self.configuration.enabled = False
        self.configuration.save()

        send_morning_message(username="test")

        self.send_notification.assert_not_called()

        morning_message = MorningMessage.objects.get()
        self.assertEqual(morning_message.user, self.user)
        self.assertEqual(morning_message.date, date.today())

    @patch.object(MorningMessageDecision, 'get_random_message_frame', return_value=None)
    def test_message_with_no_framing(self, _):
        send_morning_message(username="test")

        self.send_notification.assert_called()
        self.assertEqual(self.send_notification.call_args[1]['body'], 'Good Morning')
        sent_data = self.send_notification.call_args[1]['data']
        self.assertEqual(sent_data['body'], 'Good Morning')
        assert 'text' not in sent_data
        assert 'anchor' not in sent_data

    @patch.object(MorningMessageDecision, 'get_random_message_frame', return_value=MorningMessageDecision.FRAME_GAIN_ACTIVE)
    def test_message_with_framing(self, _):
        send_morning_message(username="test")

        self.send_notification.assert_called()
        sent_data = self.send_notification.call_args[1]['data']
        self.assertEqual(sent_data['body'], 'Example morning message')
        self.assertEqual(sent_data['text'], 'Example morning message')
        self.assertEqual(sent_data['anchor'], 'Anchor message')


class MorningMessageSurveyTests(MorningMessageTestBase):

    def setUp(self):
        super().setUp()
        
        MorningMessageQuestion.objects.create(
            name = 'first morning message',
            label = 'This is a morning message'
        )
        MorningMessageQuestion.objects.create(
            name = 'Second morning message',
            label = 'Foo bar'
        )

    def test_morning_message_creates_survey(self):
        MorningMessage.objects.create(
            user = self.user,
            date = date.today()
        )

        morning_message = MorningMessage.objects.get()
        survey = MorningMessageSurvey.objects.get()
        self.assertIsNotNone(morning_message.survey)
        self.assertEqual(morning_message.survey.id, survey.id)
        self.assertEqual(len(survey.questions), 2)

    def test_new_morning_message_survey_has_word_set(self):
        survey = MorningMessageSurvey.objects.create(
            user = self.user
        )

        self.assertEqual(len(survey.word_set), 4)

class MorningMessageSurveyViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            date_joined = datetime(2019, 5, 1).astimezone(pytz.UTC)
        )
        self.client.force_authenticate(user=self.user)
        self.configuration = Configuration.objects.create(user=self.user)
        MorningMessageTemplate.objects.create(
            body = 'Example morning message',
            anchor_message = 'Anchor message'
        )

        word_set_patch = patch.object(MorningMessageSurvey, 'get_word_set')
        self.word_set = word_set_patch.start()
        self.addCleanup(word_set_patch.stop)
        self.word_set.return_value = ['one', 'two', 'three', 'four']

    def test_get_survey(self):
        MorningMessage.objects.create(
            user = self.user,
            date = date(2019, 5, 5)
        )

        response = self.client.get(reverse('morning-messages-survey', kwargs={
            'day': '2019-5-5'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['completed'])
        self.assertEqual(response.data['wordSet'], ['one', 'two', 'three', 'four'])

    def test_get_completed_survey(self):
        morning_message = MorningMessage.objects.create(
            user = self.user,
            date = date(2019, 5, 5)
        )
        morning_message.survey.selected_word = 'one'
        morning_message.survey.save()

        response = self.client.get(reverse('morning-messages-survey', kwargs={
            'day': '2019-5-5'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['completed'])

    def test_post_survey(self):
        MorningMessage.objects.create(
            user = self.user,
            date = date(2019, 5, 5)
        )

        response = self.client.post(
            reverse('morning-messages-survey', kwargs={
                'day': '2019-5-5'
            }),
            {
                'selected_word': 'one'
            }
        )

        self.assertEqual(response.status_code, 200)
        survey = MorningMessageSurvey.objects.get()
        self.assertEqual(survey.selected_word, 'one')
