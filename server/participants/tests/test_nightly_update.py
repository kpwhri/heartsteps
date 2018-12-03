import pytz
from unittest.mock import patch

from django.test import TestCase, override_settings

from fitbit_api.models import FitbitAccount
from fitbit_api.services import FitbitDayService, FitbitClient
from locations.services import LocationService

from participants.models import Participant, User
from participants.tasks import nightly_update

@override_settings(PARTICIPANT_NIGHTLY_UPDATE_TIME='2:00')
class NightlyUpdateTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.participant = Participant.objects.create(user=self.user)

        location_service_patch = patch.object(LocationService, 'get_current_timezone')
        location_service_timezone = location_service_patch.start()
        location_service_timezone.return_value = pytz.UTC
        self.addCleanup(location_service_patch.stop)

        FitbitAccount.objects.create(
            user = self.user,
            fitbit_user = "test"
        )
        fitbit_day_patch = patch.object(FitbitDayService, 'update')
        self.fitbit_day_update = fitbit_day_patch.start()
        self.addCleanup(fitbit_day_patch.stop)
        fitbit_client_timezone_patch = patch.object(FitbitClient, 'get_timezone')
        fitbit_client_timezone = fitbit_client_timezone_patch.start()
        fitbit_client_timezone.return_value = pytz.UTC
        self.addCleanup(fitbit_client_timezone_patch.stop)
    
    def test_fitbit_gets_updated(self):

        nightly_update(username=self.user.username)

        self.fitbit_day_update.assert_called()

