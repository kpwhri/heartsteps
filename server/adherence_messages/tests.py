from datetime import date
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.test import override_settings
from django.utils import timezone

from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from fitbit_api.services import FitbitService
from page_views.models import PageView
from fitbit_api.models import FitbitConsumerKey
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
        FitbitConsumerKey.objects.update_or_create(key='key', secret='secret')
        initialize_adherence_patch = patch.object(initialize_adherence_task, 'apply_async')
        self.initialize_adherence_task = initialize_adherence_patch.start()
        self.addCleanup(initialize_adherence_patch.stop)

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
        FitbitConsumerKey.objects.update_or_create(key='key', secret='secret')
        message_send_patch = patch.object(SMSService, 'send')
        self.send_sms_message = message_send_patch.start()
        self.send_sms_message.side_effect = send_sms
        self.addCleanup(message_send_patch.stop)

        initialize_adherence_patch = patch.object(initialize_adherence_task, 'apply_async')
        self.initialize_adherence_task = initialize_adherence_patch.start()
        self.addCleanup(initialize_adherence_patch.stop)

        wore_fitbit_patch = patch.object(FitbitDay, 'get_wore_fitbit')
        self.addCleanup(wore_fitbit_patch.stop)
        self.wore_fitbit = wore_fitbit_patch.start()
        self.wore_fitbit.return_value = True

        self.user = User.objects.create(username='test')
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )

        self.account = FitbitAccount.objects.create(fitbit_user='test')
        FitbitAccountUser.create_or_update(
            user = self.user,
            account = self.account
        )

        SMSContact.objects.create(
            user = self.user,
            number = 'my-phone-number'
        )

    def create_adherence_message(self, category=None, created=None, body='foo'):

        message = AdherenceMessage(
            user = self.user,
            body = body
        )
        if category:
            message.category = category
        message.save()
        if created:
            message.created = created
            message.save()
        return message

    def patch_adherence_service(self, method):
        patched_method = patch.object(AdherenceService, method)
        mock = patched_method.start()
        self.addCleanup(patched_method.stop)
        return mock


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

    def test_will_send_if_no_message_recently_sent(self):
        message = AdherenceMessage.objects.create(
            user = self.user,
            body = 'Previously sent message'
        )
        message.created = timezone.now() - timedelta(days=1)
        message.save()

        service = AdherenceService(configuration = self.configuration)
        service.create_adherence_message(
            body = 'Example message',
            category = AdherenceMessage.APP_USED    
        )

        self.assertEqual(AdherenceMessage.objects.count(), 2)

    def test_will_not_send_if_more_than_two_messages_in_4_days(self):
        self.create_adherence_message(
            created = timezone.now() - timedelta(days=3)
        )
        self.create_adherence_message(
            created = timezone.now() - timedelta(days=1)
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

        self.assertEqual(AdherenceMessage.objects.count(), 2)
    
    def test_will_send_thrid_message_after_fourth_day(self):
        self.create_adherence_message(
            created = timezone.now() - timedelta(days=4)
        )
        self.create_adherence_message(
            created = timezone.now() - timedelta(days=3)
        )

        service = AdherenceService(configuration = self.configuration)
        service.create_adherence_message(
            body = 'Example message',
            category = AdherenceMetric.APP_USED
        )

        self.assertEqual(AdherenceMessage.objects.count(), 3)


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
        
        fitbit_service_patch = patch.object(FitbitService, 'was_updated_on')
        self.fitbit_was_update_on = fitbit_service_patch.start()
        self.fitbit_was_update_on.return_value = True
        self.addCleanup(fitbit_service_patch.stop)

        self.fitbit_last_update_time = self.patch_adherence_service('last_fitbit_update_time')
        self.fitbit_last_update_time.return_value = timezone.now()

    def test_updates_fitbit_updated(self):

        service = AdherenceService(user = self.user)
        service.update_adherence()

        metric = AdherenceMetric.objects.get(
            user = self.user,
            category = AdherenceMetric.FITBIT_UPDATED
        )
        self.assertTrue(metric.value) 
        self.assertEqual(metric.date, date.today())

    # @override_settings(STUDY_PHONE_NUMBER='(555) 555-5555')
    # @patch('adherence_messages.services.render_to_string', return_value='Example text')
    # def test_send_adherence_message_after_2_days(self, render_to_string):
    #     self.fitbit_last_update_time.return_value = timezone.now() - timedelta(days=2)

    #     service = AdherenceService(user = self.user)
    #     service.send_adherence_message()

    #     message = AdherenceMessage.objects.get(
    #         user = self.user,
    #         category = AdherenceMessage.FITBIT_UPDATED
    #     )
    #     self.assertEqual(message.body, 'Example text')
    #     render_to_string.assert_called_with(
    #         template_name = 'adherence_messages/fitbit-not-updated.txt',
    #         context = {
    #             'study_phone_number': '(555) 555-5555'
    #         }
    #     )

    # def test_sends_second_adherence_message(self):
    #     self.fitbit_last_update_time.return_value = timezone.now() - timedelta(days=3)
    #     self.create_adherence_message(
    #         category = AdherenceMessage.FITBIT_UPDATED,
    #         created = timezone.now() - timedelta(days=1)
    #     )

    #     service = AdherenceService(user = self.user)
    #     service.send_adherence_message()

    #     message_query = AdherenceMessage.objects.filter(
    #         user = self.user,
    #         category = AdherenceMessage.FITBIT_UPDATED
    #     )
    #     self.assertEqual(message_query.count(), 2)

    def test_does_not_send_more_than_2_messages(self):
        self.fitbit_last_update_time.return_value = timezone.now() - timedelta(days=4)
        self.create_adherence_message(
            category = AdherenceMessage.FITBIT_UPDATED,
            created = timezone.now() - timedelta(days=2)
        )
        self.create_adherence_message(
            category = AdherenceMessage.FITBIT_UPDATED,
            created = timezone.now() - timedelta(days=1)
        )

        service = AdherenceService(user = self.user)
        service.send_adherence_message()

        message_query = AdherenceMessage.objects.filter(
            user = self.user,
            category = AdherenceMessage.FITBIT_UPDATED
        )
        self.assertEqual(message_query.count(), 2)

class FitbitWornTests(AdherenceTaskTestBase):

    def setUp(self):
        super().setUp()
        FitbitConsumerKey.objects.update_or_create(key='key', secret='secret')
        self.patch_adherence_service('send_fitbit_not_updated_message')

    def test_updates_fitbit_worn(self):
        FitbitDay.objects.create(
            account = self.account,
            date = date.today()
        )

        service = AdherenceService(user = self.user)
        service.update_adherence()

        metric = AdherenceMetric.objects.get(
            user = self.user,
            category = AdherenceMetric.FITBIT_WORN
        )
        self.assertTrue(metric.value)
        self.assertEqual(metric.date, date.today())

    # @override_settings(STUDY_PHONE_NUMBER='(555) 555-5555')
    # @patch('adherence_messages.services.render_to_string', return_value='Example text')
    # def test_send_adherence_message_after_2_days(self, render_to_string):
    #     # Add previous message, which will be ignored
    #     self.create_adherence_message(
    #         category = AdherenceMessage.FITBIT_WORN,
    #         created = timezone.now() - timedelta(days=3)
    #     )
    #     heart_rate = FitbitMinuteHeartRate.objects.create(
    #         account = self.account,
    #         heart_rate = 20,
    #         time = timezone.now() - timedelta(days=2)
    #     )

    #     service = AdherenceService(user = self.user)
    #     service.send_adherence_message()

    #     message = AdherenceMessage.objects.get(
    #         user = self.user,
    #         category = AdherenceMessage.FITBIT_WORN,
    #         created__gt = heart_rate.time
    #     )
    #     self.assertEqual(message.body, 'Example text')
    #     render_to_string.assert_called_with(
    #         template_name = 'adherence_messages/fitbit-not-worn.txt',
    #         context = {
    #             'study_phone_number': '(555) 555-5555'
    #         }
    #     )

    # def test_sends_second_message_after_4_days(self):
    #     FitbitMinuteHeartRate.objects.create(
    #         account = self.account,
    #         heart_rate = 20,
    #         time = timezone.now() - timedelta(days=4)
    #     )
    #     self.create_adherence_message(
    #         category = AdherenceMessage.FITBIT_WORN,
    #         created = timezone.now() - timedelta(days=2)
    #     )

    #     service = AdherenceService(user = self.user)
    #     service.send_adherence_message()

    #     messages = AdherenceMessage.objects.filter(
    #         user = self.user,
    #         category = AdherenceMessage.FITBIT_WORN
    #     ).all()
    #     self.assertEqual(len(messages), 2)

    def test_does_not_send_second_message_until_2_days_after_first_message(self):
        FitbitMinuteHeartRate.objects.create(
            account = self.account,
            heart_rate = 20,
            time = timezone.now() - timedelta(days=4)
        )
        self.create_adherence_message(
            category = AdherenceMessage.FITBIT_WORN,
            created = timezone.now() - timedelta(days=1)
        )

        service = AdherenceService(user = self.user)
        service.send_adherence_message()

        messages = AdherenceMessage.objects.filter(
            user = self.user,
            category = AdherenceMessage.FITBIT_WORN
        ).all()
        self.assertEqual(len(messages), 1)

    def test_never_sends_more_than_2_messages(self):
        FitbitMinuteHeartRate.objects.create(
            account = self.account,
            heart_rate = 20,
            time = timezone.now() - timedelta(days=6)
        )
        self.create_adherence_message(
            category = AdherenceMessage.FITBIT_WORN,
            created = timezone.now() - timedelta(days=4)
        )
        self.create_adherence_message(
            category = AdherenceMessage.FITBIT_WORN,
            created = timezone.now() - timedelta(days=2)
        )

        service = AdherenceService(user = self.user)
        service.send_adherence_message()

        messages = AdherenceMessage.objects.filter(
            user = self.user,
            category = AdherenceMessage.FITBIT_WORN
        ).all()
        self.assertEqual(len(messages), 2)


class AppInstallationAdherenceTests(AdherenceTaskTestBase):

    def setUp(self):
        super().setUp()

        self.patch_adherence_service('send_fitbit_not_updated_message')
        self.patch_adherence_service('send_fitbit_not_worn_message')

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
            created = timezone.now() - timedelta(days=4)
        )
        self.create_adherence_message(
            category = AdherenceMessage.APP_INSTALLED,
            created = timezone.now() - timedelta(days=3)
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

    @override_settings(STUDY_PHONE_NUMBER='(555) 555-5555')
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
