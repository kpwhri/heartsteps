from datetime import date
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.test import override_settings
from django.utils import timezone

from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from fitbit_api.services import FitbitService
from participants.signals import initialize_participant
from participants.models import Participant
from page_views.models import PageView
from sms_messages.services import SMSService
from sms_messages.models import Message as SMSMessage
from sms_messages.models import Contact as SMSContact

from .models import AdherenceMessage
from .models import AdherenceMetric
from .models import Configuration
from .models import User
from .services import AdherenceService
from .tasks import initialize_adherence as initialize_adherence_task
from .tasks import send_adherence_message as send_adherence_message_task
from .tasks import update_adherence as update_adherence_task

@override_settings(ADHERENCE_MESSAGE_TIME='13:22')
class AdherenceConfigurationTests(TestCase):

    def setUp(self):
        initialize_adherence_patch = patch.object(initialize_adherence_task, 'apply_async')
        self.initialize_adherence_task = initialize_adherence_patch.start()
        self.addCleanup(initialize_adherence_patch.stop)

    def test_participant_initialization_enables_configuration(self):
        user = User.objects.create(
            username = 'test'
        )
        participant = Participant.objects.create(
            heartsteps_id = 'test',
            user = user
        )

        initialize_participant.send(
            sender = Participant,
            participant = participant
        )

        configuration = Configuration.objects.get(
            user = user
        )
        self.assertTrue(configuration.enabled)
        self.assertTrue(configuration.daily_task.enabled)
        self.assertEqual(configuration.daily_task.hour, 13)
        self.assertEqual(configuration.daily_task.minute, 22)

    def test_participant_initialize_reenables_configuration(self):
        user = User.objects.create(
            username = 'test'
        )
        Configuration.objects.create(
            user = user,
            enabled = False
        )
        participant = Participant.objects.create(
            heartsteps_id = 'test',
            user = user
        )

        initialize_participant.send(
            sender = Participant,
            participant = participant
        )

        configuration = Configuration.objects.get(user = user)
        self.assertTrue(configuration.enabled)

    def test_configuration_gets_disabled(self):
        user = User.objects.create(
            username = 'test'
        )
        configuration = Configuration.objects.create(
            user = user
        )

        self.assertTrue(configuration.enabled)
        self.assertTrue(configuration.daily_task.enabled)

        configuration.enabled = False
        configuration.save()

        self.assertFalse(configuration.enabled)
        self.assertFalse(configuration.daily_task.enabled)

def send_sms(body):
    return SMSMessage.objects.create(
        recipient = 'test-phone-number',
        sender = 'other-phone-number',
        body = body
    )

class AdherenceTaskTestBase(TestCase):
    
    def setUp(self):
        message_send_patch = patch.object(SMSService, 'send')
        self.send_sms_message = message_send_patch.start()
        self.send_sms_message.side_effect = send_sms
        self.addCleanup(message_send_patch.stop)

        initialize_adherence_patch = patch.object(initialize_adherence_task, 'apply_async')
        self.initialize_adherence_task = initialize_adherence_patch.start()
        self.addCleanup(initialize_adherence_patch.stop)

        self.user = User.objects.create(username='test')
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )

        self.account = FitbitAccount.objects.create(fitbit_user='test')
        FitbitAccountUser.objects.create(
            user = self.user,
            account = self.account
        )

        SMSContact.objects.create(
            user = self.user,
            number = 'my-phone-number'
        )

    def create_adherence_message(self, category, created):
        message = AdherenceMessage.objects.create(
            user = self.user,
            category = category,
            body = 'foo'
        )
        message.created = created
        message.save()
        return message


class AdherenceInitializationTests(AdherenceTaskTestBase):

    def test_new_configuration_initializes_adherence(self):
        configuration = Configuration.objects.create(
            user = User.objects.create(username='participant'),
            enabled = False
        )

        self.initialize_adherence_task.assert_called_with(
            kwargs = {
                'username': 'participant'
            }
        )
        # First call is from setup, second is from test
        self.assertEqual(self.initialize_adherence_task.call_count, 2)

        configuration.enabled = True
        configuration.save()

        # Ensureing initialize is only called when configuration is created
        self.assertEqual(self.initialize_adherence_task.call_count, 2)

    def test_recreates_adherence(self):
        self.user.date_joined = timezone.now() - timedelta(days=3)
        self.user.save()

        initialize_adherence_task(username='test')

        dates_with_adherence = []
        for metric in AdherenceMetric.objects.order_by('-date').all():
            if metric.date not in dates_with_adherence:
                dates_with_adherence.append(metric.date)
        self.assertEqual(dates_with_adherence, [date.today() - timedelta(days=offset) for offset in range(3)])

class AdherenceServiceMessagesTests(AdherenceTaskTestBase):
    
    def test_sends_adherence_alert(self):

        service = AdherenceService(configuration = self.configuration)
        service.create_adherence_message(
            body = 'Example message',
            category = AdherenceMessage.APP_USED    
        )

        message = AdherenceMessage.objects.get()
        self.assertEqual(message.category, AdherenceMessage.APP_USED)
        self.assertEqual(message.body, 'Example message')

    def test_does_not_send_adherence_alert_if_disabled(self):
        self.configuration.enabled = False
        self.configuration.save()

        service = AdherenceService(configuration = self.configuration)

        try:
            service.create_adherence_message(
                body = 'Example message',
                category = AdherenceMessage.APP_USED 
            )
            self.fail('Should not have sent message')
        except AdherenceService.AdherenceMessageDisabled:        
            pass

    def test_does_not_send_if_message_recently_sent(self):
        AdherenceMessage.objects.create(
            user = self.user,
            body = 'Previously sent message'
        )

        try:
            service = AdherenceService(configuration = self.configuration)
            service.create_adherence_message(
                body = 'Example message',
                category = AdherenceMessage.APP_USED    
            )
            self.fail('Should not have sent message')
        except AdherenceService.AdherenceMessageRecentlySent:
            pass

        self.assertEqual(AdherenceMessage.objects.count(), 1)

    @override_settings(ADHERENCE_MESSAGE_BUFFER_HOURS=2)
    def test_will_send_if_no_message_recently_sent(self):
        message = AdherenceMessage.objects.create(
            user = self.user,
            body = 'Previously sent message'
        )
        message.created = timezone.now() - timedelta(hours=3)
        message.save()

        service = AdherenceService(configuration = self.configuration)
        service.create_adherence_message(
            body = 'Example message',
            category = AdherenceMessage.APP_USED    
        )

        self.assertEqual(AdherenceMessage.objects.count(), 2)


class AdherenceTaskTests(AdherenceTaskTestBase):

    @patch.object(AdherenceService, 'update_adherence')
    def test_update_adherence(self, update_adherence):

        update_adherence_task(
            username = self.user.username
        )

        update_adherence.assert_called()



    @patch.object(AdherenceService, 'send_adherence_message')
    def test_send_adherence_message(self, send_adherence_message):

        send_adherence_message_task(
            username = self.user.username
        )

        send_adherence_message.assert_called()

class FitbitUpdatedTests(AdherenceTaskTestBase):

    def setUp(self):
        super().setUp()

        fitbit_updated_on_patch = patch.object(FitbitService, 'was_updated_on')
        self.addCleanup(fitbit_updated_on_patch.stop)
        self.fitbit_was_update_on = fitbit_updated_on_patch.start()
        self.fitbit_was_update_on.return_value = True


    def test_updates_fitbit_updated(self):

        service = AdherenceService(user = self.user)
        service.update_adherence()

        metric = AdherenceMetric.objects.get(
            user = self.user,
            category = AdherenceMetric.FITBIT_UPDATED
        )
        self.assertTrue(metric.value) 
        self.assertEqual(metric.date, date.today())

class AppInstallationAdherenceTests(AdherenceTaskTestBase):

    def setUp(self):
        super().setUp()

        wore_fitbit_patch = patch.object(FitbitDay, 'get_wore_fitbit')
        self.addCleanup(wore_fitbit_patch.stop)
        self.wore_fitbit = wore_fitbit_patch.start()
        self.wore_fitbit.return_value = True

    def test_app_installation_checked_with_update(self):
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now()
        )

        update_adherence_task(
            username = self.user.username
        )

        metric = AdherenceMetric.objects.get(
            user = self.user,
            category = AdherenceMetric.APP_INSTALLED
        )
        self.assertEqual(metric.date, date.today())
        self.assertTrue(metric.value)

    @patch('adherence_messages.services.render_to_string', return_value='Example text')
    def test_send_adherence_message_if_7_days_fitbit_and_no_install(self, render_to_string):
        self.user.date_joined = timezone.now() - timedelta(days=9)
        self.user.save()
        for day in [date.today() - timedelta(days=offset) for offset in range(8)]:
            FitbitDay.objects.create(
                account = self.account,
                date = day
            )

        service = AdherenceService(user = self.user)
        service.send_adherence_message()

        message = AdherenceMessage.objects.get()
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.category, AdherenceMessage.APP_INSTALLED)
        self.assertEqual(message.body, 'Example text')
        render_to_string.assert_called_with(
            template_name = 'adherence_messages/app-installed.txt'
        )

    def test_does_not_send_adherence_message_if_installed(self):
        self.user.date_joined = timezone.now() - timedelta(days=7)
        self.user.save()
        for day in [date.today() - timedelta(days=offset) for offset in range(7)]:
            FitbitDay.objects.create(
                account = self.account,
                date = day
            )
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now()
        )

        service = AdherenceService(user = self.user)
        service.send_adherence_message()

        self.assertEqual(AdherenceMessage.objects.count(), 0)

    def test_send_adherence_message_sends_only_3_messages(self):
        self.user.date_joined = timezone.now() - timedelta(days=10)
        self.user.save()
        for day in [date.today() - timedelta(days=offset) for offset in range(10)]:
            FitbitDay.objects.create(
                account = self.account,
                date = day
            )
        self.create_adherence_message(
            category = AdherenceMessage.APP_INSTALLED,
            created = timezone.now() - timedelta(days=2)
        )
        self.create_adherence_message(
            category = AdherenceMessage.APP_INSTALLED,
            created = timezone.now() - timedelta(days=1)
        )

        service = AdherenceService(user = self.user)
        service.send_adherence_message()
        
        self.assertEqual(AdherenceMessage.objects.count(), 3)

        service.send_adherence_message()

        self.assertEqual(AdherenceMessage.objects.count(), 3)

class AppUsedAdherenceTests(AdherenceTaskTestBase):

    def test_app_used_checked_nightly(self):
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now()
        )

        service = AdherenceService(configuration = self.configuration)
        service.update_adherence()

        metric = AdherenceMetric.objects.get(
            user = self.user,
            category = AdherenceMetric.APP_USED    
        )
        self.assertEqual(metric.date, date.today())

    @override_settings(STUDY_PHONE_NUMBER='(555) 555-5555')
    @patch('adherence_messages.services.render_to_string', return_value='Example text')
    @patch.object(AdherenceMessage, 'send')
    @patch.object(AdherenceService, 'send_fitbit_not_updated_message')
    def test_adherence_message_sent_no_use_4_days(self, fitbit_udpated, adherence_messsage_send, render_to_string):
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now() - timedelta(days=4, minutes=1)
        )

        service = AdherenceService(configuration = self.configuration)
        service.send_adherence_message()

        message = AdherenceMessage.objects.get(
            user = self.user,
            category = 'app-used'
        )
        self.assertEqual(message.body, 'Example text')
        render_to_string.assert_called_with(
            template_name = 'adherence_messages/app-used.txt',
            context = {
                'study_phone_number': '(555) 555-5555'
            }
        )
        adherence_messsage_send.assert_called()

    def test_adherence_message_sent_once(self):
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now() - timedelta(days = 8)
        )
        message = AdherenceMessage.objects.create(
            user = self.user,
            category = AdherenceMessage.APP_USED,
            body = 'foo bar'
        )
        message.created = timezone.now() - timedelta(days=5)
        message.save()

        service = AdherenceService(configuration = self.configuration)
        service.send_adherence_message()

        message_count = AdherenceMessage.objects.filter(
            user = self.user,
            category = AdherenceMessage.APP_USED
        ).count()
        self.assertEqual(message_count, 1)

    def test_adherence_message_sent_if_newly_non_adherent(self):
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now() - timedelta(days = 9)
        )
        message = AdherenceMessage.objects.create(
            user = self.user,
            category = AdherenceMessage.APP_USED,
            body = 'foo bar'
        )
        message.created = timezone.now() - timedelta(days=5)
        message.save()
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now() - timedelta(days = 5)
        )

        service = AdherenceService(configuration = self.configuration)
        service.send_adherence_message()

        self.assertEqual(AdherenceMessage.objects.count(), 2)
