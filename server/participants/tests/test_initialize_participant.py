from datetime import timedelta
from django.test import TestCase, override_settings
from django.utils import timezone
from unittest.mock import patch


from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from daily_tasks.models import DailyTask
from anti_sedentary.models import Configuration as AntiSedentaryConfiguration
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from fitbit_api.models import FitbitAccountUpdate
from morning_messages.models import Configuration as MorningMessageConfiguration
from walking_suggestion_times.models import SuggestionTime
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration

from participants.models import Cohort
from participants.models import Participant, User, TASK_CATEGORY
from participants.services import ParticipantService

class ParticipantConfiguration(TestCase):

    def setUp(self):
        self.cohort = Cohort.objects.create(
            name='test'
        )
        self.participant = Participant.objects.create(
            heartsteps_id = 'test',
            cohort = self.cohort
        )

    def test_enroll_participant_creates_user(self):
        self.assertEqual(self.participant.user, None)

        self.participant.enroll()

        self.assertEqual(self.participant.user.username, 'test')
        self.assertTrue(self.participant.user.is_active)

    def test_disabling_participant_updates_user(self):
        self.participant.enroll()

        self.participant.disable()

        self.assertFalse(self.participant.enabled)
        self.assertFalse(self.participant.active)
        self.assertFalse(self.participant.user.is_active)

    def test_disabled_participant_can_be_enabled(self):
        self.participant.enroll()
        self.participant.disable()

        self.participant.enable()

        self.assertTrue(self.participant.enabled)
        self.assertTrue(self.participant.active)
        self.assertTrue(self.participant.user.is_active)

    def test_study_start_is_none_by_default(self):
        self.assertEqual(self.participant.study_start, None)

    def test_study_start_is_first_fitbit_account_update(self):
        self.participant.enroll()
        fitbit_account = FitbitAccount.objects.create(fitbit_user='test')
        FitbitAccountUser.objects.create(
            account=fitbit_account,
            user=self.participant.user
        )
        account_update = FitbitAccountUpdate.objects.create(account = fitbit_account)
        account_update.created = timezone.now() - timedelta(days=2)
        account_update.save()
        self.participant.user.date_joined = self.participant.user.date_joined - timedelta(days=2)
        self.participant.user.save()
        
        diff_study_start = timezone.now() - self.participant.study_start
        self.assertEqual(diff_study_start.days, 2)

    def test_study_end_date_is_none_by_default(self):
        self.participant.enroll()
        fitbit_account = FitbitAccount.objects.create(fitbit_user='test')
        FitbitAccountUser.objects.create(
            account=fitbit_account,
            user=self.participant.user
        )
        account_update = FitbitAccountUpdate.objects.create(account = fitbit_account)

        start_of_account_update_day = account_update.created.replace(
            hour = 0,
            minute = 0,
            second = 0,
            microsecond = 0
        )
        self.assertEqual(self.participant.study_start, start_of_account_update_day)
        self.assertIsNone(self.participant.study_end)

    def test_study_end_date_calculated_from_cohort_date(self):
        self.participant.enroll()
        fitbit_account = FitbitAccount.objects.create(fitbit_user='test')
        FitbitAccountUser.objects.create(
            account=fitbit_account,
            user=self.participant.user
        )
        account_update = FitbitAccountUpdate.objects.create(account = fitbit_account)
        self.cohort.study_length = 77
        self.cohort.save()
        
        diff = self.participant.study_end - timezone.now()
        self.assertEqual(diff.days, self.cohort.study_length)
        

@override_settings(PARTICIPANT_NIGHTLY_UPDATE_TIME='4:15')
class InitializeTask(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.participant = Participant.objects.create(
            heartsteps_id = 'test',
            user = self.user
        )

        baseline_complete_patch = patch.object(ParticipantService, 'is_baseline_complete')
        self.baseline_complete = baseline_complete_patch.start()
        self.baseline_complete.return_value=True
        self.addCleanup(baseline_complete_patch.stop)

    def test_starts_nightly_update_task(self):
        service = ParticipantService(username="test")
        service.initialize()

        daily_task = DailyTask.objects.get(user__username="test", category=TASK_CATEGORY)
        self.assertEqual(daily_task.hour, 4)
        self.assertEqual(daily_task.minute, 15)
    
    def test_creates_walking_suggestion_configuration(self):
        service = ParticipantService(username="test")
        service.initialize()

        configuration = WalkingSuggestionConfiguration.objects.get(user__username="test")
        self.assertIsNotNone(configuration)

    def test_creates_morning_message_configuration(self):
        service = ParticipantService(username="test")
        service.initialize()

        configuration = MorningMessageConfiguration.objects.get()
        self.assertEqual(configuration.user.username, "test")

    def test_creates_anti_sedentary_configuration(self):
        service = ParticipantService(username="test")
        service.initialize()

        configuration = AntiSedentaryConfiguration.objects.get()
        self.assertEqual(configuration.user.username, "test")

    def test_creates_adherence_message_configuration(self):
        service = ParticipantService(username="test")
        service.initialize()

        configuration = AdherenceMessageConfiguration.objects.get()
        self.assertEqual(configuration.user.username, "test")
        self.assertTrue(configuration.enabled)

    def test_enables_adherence_message_configuration(self):
        AdherenceMessageConfiguration.objects.create(
            user = self.user,
            enabled = False
        )

        service = ParticipantService(username="test")
        service.initialize()

        configuration = AdherenceMessageConfiguration.objects.get()
        self.assertEqual(configuration.user.username, "test")
        self.assertTrue(configuration.enabled)

    def test_creates_default_walking_suggestion_times(self):
        service = ParticipantService(username="test")
        service.initialize()

        suggestion_times = SuggestionTime.objects.filter(user=self.user).all()
        self.assertEqual(len(suggestion_times), 5)

    def test_does_not_change_existing_walking_suggestion_times(self):
        SuggestionTime.objects.create(
            user = self.user,
            category = SuggestionTime.MORNING,
            hour = 1,
            minute = 0
        )

        service = ParticipantService(username="test")
        service.initialize()

        suggestion_times = SuggestionTime.objects.filter(user=self.user).all()
        self.assertEqual(len(suggestion_times), 1)
