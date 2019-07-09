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

    def test_update_adherence(self):

        update_adherence_task(
            username = self.user.username
        )

        adherence_day = AdherenceDay.objects.get()
        self.assertEqual(adherence_day.date, date.today())
        self.assertEqual(adherence_day.user, self.user)

class AppInstallationAdherenceTests(AdherenceTaskTestBase):

    def test_app_installation_checked_nightly(self):
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now()
        )

        update_adherence_task(
            username = self.user.username
        )

        adherence = AdherenceDay.objects.get(user = self.user)
        self.assertEqual(adherence.date, date.today())
        self.assertTrue(adherence.app_installed)

    @patch.object(AdherenceService, 'get_message_text_for', return_value='Example text')
    def test_send_adherence_message_if_7_days_fitbit_and_no_install(self, get_message_text_for):
        for offset in range(7):
            adherence = AdherenceDay.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset)
            )
            adherence.set_metric('app-installed', False)
            adherence.set_metric('wore-fitbit', True)

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        message = AdherenceMessage.objects.get()
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.category, 'app-installed')
        self.assertEqual(message.body, 'Example text')
        get_message_text_for.assert_called_with('app-installed')

    def test_does_not_send_adherence_message_if_installed(self):
        for offset in range(7):
            adherence = AdherenceDay.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset)
            )
            adherence.set_metric('app-installed', False)
            adherence.set_metric('wore-fitbit', True)
        adherence = AdherenceDay.objects.get(
            user = self.user,
            date = date.today()
        )
        adherence.set_metric('app-installed', True)
        adherence.set_metric('wore-fitbit', True)

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        self.assertEqual(AdherenceMessage.objects.count(), 0)       

    def test_send_adherence_message_sends_only_3_messages(self):
        for offset in range(9):
            adherence = AdherenceDay.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset)
            )
            adherence.set_metric('app-installed', False)
            adherence.set_metric('wore-fitbit', True)
        AdherenceMessage.objects.create(
            user = self.user,
            category = 'app-installed',
            body = 'first message'
        )
        AdherenceMessage.objects.create(
            user = self.user,
            category = 'app-installed',
            body = 'second message'
        )

        service = DailyAdherenceService(configuration = self.configuration)
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
        adherence = AdherenceDay.objects.create(
            user = self.user,
            date = date.today() - timedelta(days=4)
        )
        adherence.app_installed = True
        adherence.app_used = True
        for offset in range(4):
            adherence = AdherenceDay.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset)
            )
            adherence.set_metric('app-installed', True)
            adherence.set_metric('app-used', False)


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
        adherence = AdherenceDay.objects.create(
            user = self.user,
            date = date.today() - timedelta(days=10)
        )
        adherence.app_installed = True
        adherence.app_used = True
        # Add previous adherence message before last time used
        # to ensure this message is ignored
        message = AdherenceMessage.objects.create(
            user = self.user,
            category = 'app-used'
        )
        message.created = timezone.now() - timedelta(days=11)
        message.save()
        # Add many fake days
        for offset in range(10):
            adherence = AdherenceDay.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset)
            )
            adherence.set_metric('app-installed', True)
            adherence.set_metric('app-used', False)
        AdherenceMessage.objects.create(
            user = self.user,
            category = 'app-used',
            created = timezone.now() - timedelta(days=6)
        )

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        # Messages from -11 days and -6 days
        self.assertEqual(AdherenceMessage.objects.count(), 2)
