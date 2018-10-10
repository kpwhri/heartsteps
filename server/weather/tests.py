from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from weather.darksky_api_manager import DarkSkyApiManager
from weather.models import WeatherForecast
from weather.services import WeatherService

class WeatherServiceTest(TestCase):

    def get_forecast(self, latitude, longitude):
        return {
            'latitude': 123.123,
            'longitude': 42.42,
            'time': timezone.now(),
            'precip_probability': 30,
            'precip_type': 'rain',
            'temperature': 20,
            'apparent_temperature': 20
        }

    @patch.object(DarkSkyApiManager, 'get_hour_forecast', get_forecast)
    def test_generates_forecast_from_darksky(self):
        forecast = WeatherService.make_forecast(123, 456)

        self.assertEqual(forecast.precip_type, 'rain')

    def test_get_context_for_forecast(self):
        forecast = WeatherForecast.objects.create(
            latitude = 123,
            longitude = 42,
            time = timezone.now(),
            precip_probability = 15,
            precip_type = 'rain',
            temperature = 50,
            apparent_temperature = 56
        )

        context = WeatherService.get_forecast_context(forecast)

        self.assertEqual(WeatherService.WEATHER_OUTDOOR, context)

    def test_get_average_context_for_forecast(self):
        forecasts = []
        forecasts.append(WeatherForecast.objects.create(
            latitude = 123,
            longitude = 42,
            time = timezone.now(),
            precip_probability = 15,
            precip_type = 'rain',
            temperature = 50,
            apparent_temperature = 56
        ))
        forecasts.append(WeatherForecast.objects.create(
            latitude = 123,
            longitude = 42,
            time = timezone.now(),
            precip_probability = 15,
            precip_type = 'snow',
            temperature = 50,
            apparent_temperature = 56
        ))

        context = WeatherService.get_average_forecast_context(forecasts)

        self.assertEqual(WeatherService.WEATHER_OUTDOOR_SNOW, context)
