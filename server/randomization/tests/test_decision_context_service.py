from unittest.mock import patch
import pytz
from datetime import datetime
from timezonefinder import TimezoneFinder

from django.test import TestCase
from django.utils import timezone

from django.contrib.auth.models import User

from locations.models import Location, Place
from locations.services import LocationService
from weather.models import WeatherForecast
from weather.services import WeatherService

from randomization.services import DecisionContextService
from randomization.models import Decision, DecisionContext

class DecisionContextTest(TestCase):
    """
    Ensure decisions are created and gather context from associated services.
    """

    def setUp(self):
        self.user = User.objects.create(username="test")

        get_last_location_patch = patch.object(LocationService, 'get_last_location')
        self.addCleanup(get_last_location_patch.stop)
        self.get_last_location = get_last_location_patch.start()
        self.get_last_location.return_value = Location.objects.create(
            longitude = 123.123,
            latitude = 42.42,
            user = self.user,
            time = timezone.now()
        )

    def make_decision_service(self, time=None):
        if not time:
            time = timezone.now()
        decision = Decision.objects.create(
            user = self.user,
            time = time
        )
        return DecisionContextService(decision)

    @patch.object(DecisionContextService, 'get_location_context', return_value="home")
    @patch.object(DecisionContextService, 'get_weather_context', return_value="outdoor")
    def test_decision_adds_context(self, get_weather_context, get_location_context):
        """
        Decision service adds correct tags to decision and saves related objects
        """
        decision_service = self.make_decision_service()
        
        decision_service.update_context()

        get_weather_context.assert_called()
        get_location_context.assert_called()
        context_tags_text = [tag.tag for tag in decision_service.decision.tags.all()]
        self.assertIn('home', context_tags_text)
        self.assertIn('outdoor', context_tags_text)

    @patch.object(LocationService, 'categorize_location', return_value="home")
    def test_get_location_context(self, categorize_location):
        decision_service = self.make_decision_service()
        
        location_type = decision_service.get_location_context()

        categorize_location.assert_called()
        self.assertEqual(location_type, "home")
        self.get_last_location.assert_called()
        self.assertEqual(DecisionContext.objects.filter(decision=decision_service.decision).count(), 1)

    def test_get_location_fails(self):
        decision_service = self.make_decision_service()

        location_type = decision_service.get_location_context()

        self.assertEqual(location_type, "other")

    @patch.object(LocationService, 'get_last_location')
    def test_get_location_returns_location_in_decision_context(self, get_last_location):
        get_last_location.return_value = None
        decision_service = self.make_decision_service()
        location = Location.objects.create(
            latitude = 22.22,
            longitude = 42.42,
            user = decision_service.user,
            time = timezone.now()
        )
        DecisionContext.objects.create(
            decision = decision_service.decision,
            content_object = location
        )
        
        returned_location = decision_service.get_location()

        get_last_location.assert_not_called()
        self.assertEqual(returned_location.id, location.id)

    @patch.object(WeatherService,'get_forecast_context')
    @patch.object(WeatherService, 'make_forecast')
    def test_get_weather_context(self, make_forecast, get_forecast_context):
        fake_weather_object = User.objects.create(username="totally_fake")
        make_forecast.return_value = fake_weather_object
        get_forecast_context.return_value = 'outdoors'
        decision_service = self.make_decision_service()
        decision_service.location = Location.objects.create(
            latitude = 22.22,
            longitude = 42.42,
            user = decision_service.user,
            time = timezone.now()
        )

        weather_context = decision_service.get_weather_context()

        self.assertEqual(weather_context, "outdoors")
        get_forecast_context.assert_called_with(fake_weather_object)
        make_forecast.assert_called_with(
            latitude = 22.22,
            longitude = 42.42,
            time = decision_service.decision.time
        )
        # there should only be one saved object
        saved_decision_forecast = DecisionContext.objects.get(decision=decision_service.decision).content_object
        self.assertEqual(saved_decision_forecast, fake_weather_object)

    @patch.object(WeatherService, 'get_average_forecast_context')
    @patch.object(WeatherService, 'make_forecast')
    def test_get_weather_context_no_location(self, make_forecast, get_average_forecast_context):
        """
        Decision service imputes weather when no location is found
        """
        def unknown_location():
            raise LocationService.UnknownLocation()
        self.get_last_location.side_effect = unknown_location
        fake_weather_object = User.objects.create(username="totally_fake")
        make_forecast.return_value = fake_weather_object
        get_average_forecast_context.return_value = 'outdoors'
        decision_service = self.make_decision_service()
        Place.objects.create(
            user = decision_service.user,
            type = 'home',
            latitude = 123.456,
            longitude = 42.42
        )
        Place.objects.create(
            user = decision_service.user,
            type = 'work',
            latitude = 123.123,
            longitude = 42.05
        )

        weather_context = decision_service.get_weather_context()

        self.assertEqual(weather_context, "outdoors")
        get_average_forecast_context.assert_called()
        self.assertIn(fake_weather_object, get_average_forecast_context.call_args[0][0])

    def test_add_weekday_context(self):
        #day is a Wednesday
        decision_time = datetime(2018, 10, 10, 10, 10).astimezone(pytz.utc)
        decision_service = self.make_decision_service(decision_time)

        context = decision_service.get_week_context()
        
        self.assertEqual(context, "weekday")

    def test_add_weekend_context(self):
        # Day is Saturady
        decision_time = datetime(2018, 10, 13, 13, 13).astimezone(pytz.utc)
        decision_service = self.make_decision_service(decision_time)

        context = decision_service.get_week_context()
        
        self.assertEqual(context, "weekend")

    @patch.object(TimezoneFinder, 'timezone_at', return_value="US/Pacific")
    def test_corrects_weekend_for_timezone(self, timezone_at):
        # Day is early monday morning UTC - late sunday evening PST
        decision_time = datetime(2018, 10, 15, 2).astimezone(pytz.utc)
        decision_service = self.make_decision_service(decision_time)
        location = Location.objects.create(
            latitude = 123.123,
            longitude = 42.42,
            user = decision_service.user,
            time = timezone.now()
        )
        DecisionContext.objects.create(
            decision = decision_service.decision,
            content_object = location
        )

        context = decision_service.get_week_context()
        
        self.assertEqual(context, "weekend")
        timezone_at.assert_called_with(lat=123.123, lng=42.42)
