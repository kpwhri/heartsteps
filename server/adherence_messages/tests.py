from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.test import override_settings

from participants.signals import initialize_participant

from .models import Configuration
from .models import User
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

class AdherenceTaskTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )

    @patch.object(update_adherence_signal, 'send')
    def test_update_adherence_signal_sent(self, update_adherence_signal):

        update_adherence_task(
            username = 'test'
        )

        update_adherence_signal.assert_called_with(
            sender = User,
            user = self.user,
            date = date.today()
        )

    @patch.object(update_adherence_signal, 'send')
    def test_update_adherence_signal_sent(self, update_adherence_signal):
        self.configuration.enabled = False
        self.configuration.save()

        update_adherence_task(
            username = 'test'
        )

        update_adherence_signal.assert_not_called()
