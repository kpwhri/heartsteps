import pytz
from unittest.mock import patch
from datetime import date, timedelta

from django.test import TestCase, override_settings

from fitbit_api.models import FitbitAccount, FitbitAccountUser
from fitbit_activities.services import FitbitDayService, FitbitClient
from locations.services import LocationService

from participants.models import Participant, User
from participants.tasks import daily_update
from participants.signals import nightly_update

@override_settings(PARTICIPANT_NIGHTLY_UPDATE_TIME='2:00')
@override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example')
class NightlyUpdateTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.participant = Participant.objects.create(user=self.user)

        location_service_patch = patch.object(LocationService, 'get_current_timezone')
        location_service_timezone = location_service_patch.start()
        location_service_timezone.return_value = pytz.UTC
        self.addCleanup(location_service_patch.stop)

        fitbit_client_timezone_patch = patch.object(FitbitClient, 'get_timezone')
        fitbit_client_timezone = fitbit_client_timezone_patch.start()
        fitbit_client_timezone.return_value = pytz.UTC
        self.addCleanup(fitbit_client_timezone_patch.stop)

        nightly_update_patch = patch.object(nightly_update, 'send')
        self.nightly_update = nightly_update_patch.start()
        self.addCleanup(nightly_update_patch.stop)

    def testSendNightlyUpdateSignal(self):
        daily_update(username = self.user.username)

        self.nightly_update.assert_called_with(
            sender = User,
            user = self.user,
            day = date.today() - timedelta(days=1)
        )
    
    @patch.object(FitbitDayService, 'update')
    def testFitbitDayUpdate(self, fitbit_day_update):
        FitbitAccountUser.objects.create(
            account = FitbitAccount.objects.create(fitbit_user = "test"),
            user = self.user
        )

        daily_update(username=self.user.username)

        fitbit_day_update.assert_called()
