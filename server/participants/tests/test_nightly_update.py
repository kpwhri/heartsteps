import pytz
from unittest.mock import patch
from datetime import date, timedelta

from django.test import TestCase, override_settings

from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from adherence_messages.services import AdherenceService
from anti_sedentary.models import Configuration as AntiSedentaryConfiguration
from anti_sedentary.services import AntiSedentaryService
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from fitbit_activities.services import FitbitDayService, FitbitClient
from locations.services import LocationService
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.services import WalkingSuggestionService
from weather.services import WeatherService

from participants.models import Participant, User
from participants.tasks import daily_update

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
    
    @patch.object(FitbitDayService, 'update')
    def testFitbitDayUpdate(self, fitbit_day_update):
        FitbitAccountUser.objects.create(
            account = FitbitAccount.objects.create(fitbit_user = "test"),
            user = self.user
        )

        daily_update(username=self.user.username)

        fitbit_day_update.assert_called()

    @patch.object(AntiSedentaryService, 'update')
    def test_anti_sedentary_service_updated(self, anti_sedentary_service_update):
        AntiSedentaryConfiguration.objects.create(
            user = self.user
        )

        daily_update(username=self.user.username)

        anti_sedentary_service_update.assert_called()

    @patch.object(WalkingSuggestionService, 'nightly_update')
    def test_walking_suggestions_nightly_update(self, walking_suggestions_nightly_update):
        WalkingSuggestionConfiguration.objects.create(
            user = self.user,
            enabled = True
        )

        daily_update(username=self.user.username)

        walking_suggestions_nightly_update.assert_called()

    @patch.object(AdherenceService, 'update_adherence')
    def test_adherence_metrics_updated(self, update_adherence):
        AdherenceMessageConfiguration.objects.create(
            user = self.user
        )

        daily_update(username = self.user.username)

        update_adherence.assert_called()

    @patch.object(WeatherService, 'update_forecasts')
    @patch.object(WeatherService, 'update_daily_forecast')
    def test_updates_daily_weather_forecasts(self, update_daily_forecast, update_forecasts):

        daily_update(username = self.user.username)

        update_daily_forecast.assert_called()
        update_forecasts.assert_called()

