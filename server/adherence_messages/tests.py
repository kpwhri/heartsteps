from datetime import date
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.test import override_settings
from django.utils import timezone

from participants.signals import initialize_participant
from page_views.models import PageView

from .models import Configuration
from .models import AdherenceMessage
from .models import AdherenceMetric
from .models import User
from .services import AdherenceService
from .signals import update_adherence as update_adherence_signal
from .tasks import update_adherence as update_adherence_task

@override_settings(ADHERENCE_UPDATE_TIME='13:22')
class AdherenceConfigurationTests(TestCase):

    def test_participant_initialization_enables_configuration(self):
        user = User.objects.create(
            username = 'test'
        )

        initialize_participant.send(
            sender = User,
            user = user
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

        initialize_participant.send(
            sender = User,
            user = user
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

class AdherenceTaskTestBase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )

        message_send_patch = patch.object(AdherenceMessage, 'send')
        send_patch = message_send_patch.start()
        send_patch.return_value = 'test-1234'
        self.addCleanup(message_send_patch.stop)

class AdherenceTaskTests(AdherenceTaskTestBase):

    @patch.object(update_adherence_signal, 'send')
    def test_update_adherence(self, update_adherence_signal):

        update_adherence_task(
            username = self.user.username
        )

        update_adherence_signal.assert_called_with(
            sender = User,
            user = self.user,
            date = date.today()
        )


class AppInstallationAdherenceTests(AdherenceTaskTestBase):

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

    @patch.object(AdherenceService, 'get_message_text_for', return_value='Example text')
    def test_send_adherence_message_if_7_days_fitbit_and_no_install(self, get_message_text_for):
        for offset in range(7):
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today(),
                category = AdherenceMetric.APP_INSTALLED,
                value = False
            )
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today(),
                category = AdherenceMetric.WORE_FITBIT,
                value = True
            )

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        message = AdherenceMessage.objects.get()
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.category, 'app-installed')
        self.assertEqual(message.body, 'Example text')
        get_message_text_for.assert_called_with('app-installed')

    def test_does_not_send_adherence_message_if_installed(self):
        for offset in range(7):
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.APP_INSTALLED,
                value = False
            )
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.WORE_FITBIT,
                value = True
            )
        AdherenceMetric.objects.update_or_create(
            user = self.user,
            date = date.today(),
            category = AdherenceMetric.APP_INSTALLED,
            defaults = {
                'value': True
            }
        )

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        self.assertEqual(AdherenceMessage.objects.count(), 0)       

    def test_send_adherence_message_sends_only_3_messages(self):
        for offset in range(9):
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.APP_INSTALLED,
                value = False
            )
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.WORE_FITBIT,
                value = True
            )
        AdherenceMessage.objects.create(
            user = self.user,
            date = date.today() - timedelta(2),
            category = 'app-installed',
            body = 'first message'
        )
        AdherenceMessage.objects.create(
            user = self.user,
            date = date.today() - timedelta(1),
            category = 'app-installed',
            body = 'second message'
        )

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        self.assertEqual(AdherenceMessage.objects.count(), 3)

        service.send_message()

        self.assertEqual(AdherenceMessage.objects.count(), 3)

class AppUsedAdherenceTests(AdherenceTaskTestBase):

    def test_app_used_checked_nightly(self):
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
            category = AdherenceMetric.APP_USED    
        )
        self.assertEqual(metric.date, date.today())

    @patch.object(AdherenceService, 'get_message_text_for', return_value='Example text')
    def test_adherence_message_sent_no_use_4_days(self, get_message_text_for):
        AdherenceMetric.objects.create(
            user = self.user,
            date = date.today() - timedelta(days=4),
            category = AdherenceMetric.APP_INSTALLED,
            value = True
        )
        AdherenceMetric.objects.create(
            user = self.user,
            date = date.today() - timedelta(days=4),
            category = AdherenceMetric.APP_USED,
            value = True
        )
        for offset in range(4):
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.APP_INSTALLED,
                value = True
            )
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.APP_USED,
                value = False
            )

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        message = AdherenceMessage.objects.get(
            user = self.user,
            category = 'app-used'
        )
        self.assertEqual(message.body, 'Example text')
        get_message_text_for.assert_called_with('app-used')

    def test_adherence_message_sent_once(self):
        # Set last used day
        AdherenceMetric.objects.create(
            user = self.user,
            date = date.today() - timedelta(days=10),
            category = AdherenceMetric.APP_USED,
            value = True
        )
        AdherenceMetric.objects.create(
            user = self.user,
            date = date.today() - timedelta(days=10),
            category = AdherenceMetric.APP_INSTALLED,
            value = True
        )
        # Add previous adherence message before last time used
        # to ensure this message is ignored
        message = AdherenceMessage.objects.create(
            user = self.user,
            category = 'app-used',
            date = date.today() - timedelta(days=11)
        )
        message.created = timezone.now() - timedelta(days=11)
        message.save()
        # Add many fake days
        for offset in range(10):
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.APP_USED,
                value = False
            )
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.APP_INSTALLED,
                value = True
            )
        AdherenceMessage.objects.create(
            user = self.user,
            date = date.today() - timedelta(days=6),
            category = 'app-used',
            created = timezone.now() - timedelta(days=6)
        )

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        # Messages from -11 days and -6 days
        self.assertEqual(AdherenceMessage.objects.count(), 2)
