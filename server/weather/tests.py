from unittest.mock import patch
import json
import requests

from django.test import TestCase
from django.utils import timezone

from weather.darksky_api_manager import DarkSkyApiManager
from weather.models import WeatherForecast
from weather.services import WeatherService

class DarkSkyApiTests(TestCase):

    def mock_response(self, status_code, data):
        class MockResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self.data = data
                self.text = json.dumps(data)
            
            def json(self):
                return self.data
        return MockResponse(status_code, data)

    def setUp(self):
        self.weather_response = {
            'latitude': 10,
            'longitude': 10,
            'currently': {
                'time': 10,
                'percipProbability': 0.10,
                'precipType': 'rain',
                'temperature': 70,
                'apparentTemperature': 75,
                'windSpeed': 10.19,
                'cloudCover': 0.25
            }
        }

        requests_patch = patch.object(requests, 'get')
        self.addCleanup(requests_patch.stop)
        self.requests = requests_patch.start()
        self.requests.return_value = self.mock_response(200, self.weather_response)

    def test_get_forecast(self):
        darksky_api = DarkSkyApiManager()
        now = timezone.now()
        
        forecast = darksky_api.get_forecast(
            latitude = 12,
            longitude = 123,
            time = now
        )
        
        mock_url = darksky_api.WEATHER_URL.format(
            api_key = darksky_api.API_KEY,
            latitude = 12,
            longitude = 123,
            time = round(now.timestamp())
        )
        self.requests.assert_called_with(mock_url)
        self.assertEqual(forecast['latitude'], 10)
        self.assertEqual(forecast['precip_type'], 'rain')
        self.assertEqual(forecast['apparent_temperature'], 75)

    def test_precip_type_default_value(self):
        del self.weather_response['currently']['precipType']
        darksky_api = DarkSkyApiManager()

        forecast = darksky_api.get_forecast(
            latitude = 12,
            longitude = 123,
            time = timezone.now()
        )

        self.assertEqual(forecast['precip_type'], 'None')

class WeatherServiceTest(TestCase):

    def get_forecast(self, latitude, longitude, time):
        return {
            'latitude': 123.123,
            'longitude': 42.42,
            'time': time,
            'precip_probability': 30,
            'precip_type': 'rain',
            'temperature': 20,
            'apparent_temperature': 20
        }

    @patch.object(DarkSkyApiManager, 'get_forecast', get_forecast)
    def test_generates_forecast_from_darksky(self):
        forecast = WeatherService.make_forecast(123, 456, timezone.now())

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
