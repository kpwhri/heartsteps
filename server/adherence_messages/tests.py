from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.test import override_settings
from django.utils import timezone

from participants.signals import initialize_participant
from page_views.models import PageView

from .models import Configuration
from .models import AdherenceDay
from .models import User
from .services import DailyAdherenceService
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



