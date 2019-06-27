from datetime import date
from datetime import datetime
from datetime import timedelta
from unittest.mock import patch
import json
import requests

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from locations.services import LocationService

from .darksky_api_manager import DarkSkyApiManager
from .models import DailyWeatherForecast
from .models import WeatherForecast
from .models import User
from .services import WeatherService

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
        
        mock_url = darksky_api.make_url(
            latitude = 12,
            longitude = 123,
            time = round(now.timestamp()),
            exclude = ['hourly', 'daily', 'alerts', 'minutely', 'flags']
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

    def test_get_daily_forecast(self):
        self.requests.return_value = self.mock_response(
            status_code = 200,
            data = {
                'timezone': 'UTC',
                'daily': [
                    {
                        'time': datetime(2019,6,26).timestamp(),
                        'icon': 'rain',
                        'temperatureHigh': 67.8,
                        'temperatureLow': 45.6 
                    }
                ]
            }
        )
        darksky_api = DarkSkyApiManager()

        daily_forecast = darksky_api.get_daily_forecast(
            latitude = 12,
            longitude = 34,
            date = date(2019,6,26)
        )

        mock_url = darksky_api.make_url(
            latitude = 12,
            longitude = 34,
            exclude = ['hourly', 'currently', 'alerts', 'minutely', 'flags']
        )
        self.assertEqual(daily_forecast['date'], date(2019,6,26))
        self.assertEqual(daily_forecast['category'], DailyWeatherForecast.RAIN)
        self.assertEqual(daily_forecast['high'], 67.8)
        self.assertEqual(daily_forecast['low'], 45.6)

    def test_get_weekly_forecast(self):
        self.requests.return_value = self.mock_response(
            status_code = 200,
            data = {
                'timezone': 'UTC',
                'daily': [
                    {
                        'time': datetime(2019,6,26).timestamp(),
                        'icon': 'rain',
                        'temperatureHigh': 67.8,
                        'temperatureLow': 45.6 
                    },
                    {
                        'time': datetime(2019,6,27).timestamp(),
                        'icon': 'partialy-cloudy-day',
                        'temperatureHigh': 67.8,
                        'temperatureLow': 45.6 
                    }
                ]
            }
        )
        darksky_api = DarkSkyApiManager()

        weekly_forecast = darksky_api.get_weekly_forecast(
            latitude = 12,
            longitude = 34
        )

        mock_url = darksky_api.make_url(
            latitude = 12,
            longitude = 34,
            exclude = ['hourly', 'currently', 'alerts', 'minutely', 'flags']
        )
        self.requests.assert_called_with(mock_url)
        self.assertEqual(len(weekly_forecast), 2)
        forecast = weekly_forecast[0]
        self.assertEqual(forecast['date'], date(2019,6,26))
        self.assertEqual(forecast['category'], 'rain')
        self.assertEqual(forecast['high'], 67.8)
        self.assertEqual(forecast['low'], 45.6)

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

    @patch.object(LocationService, 'get_location_on')
    @patch.object(DarkSkyApiManager, 'get_daily_forecast')
    def test_update_daily_forecast(self, get_daily_forecast, get_location_on):
        user = User.objects.create(username="test")
        DailyWeatherForecast.objects.create(
            user = user,
            date = date.today(),
            category = DailyWeatherForecast.CLEAR,
            high = 22,
            low = 15
        )
        class MockLocation:
            latitude = 12
            longitude = 34
        get_location_on.return_value = MockLocation()
        get_daily_forecast.return_value = {
            'date': date.today(),
            'category': DailyWeatherForecast.RAIN,
            'high': 76.5,
            'low': 54.3
        }
        weather_service = WeatherService(user=user)

        forecast = weather_service.update_daily_forecast(
            date = date.today()
        )

        get_location_on.assert_called_with(date.today())
        get_daily_forecast.assert_called_with(
            date = date.today(),
            latitude = 12,
            longitude = 34
        )
        self.assertEqual(forecast.category, DailyWeatherForecast.RAIN)
        self.assertEqual(forecast.high, 76.5)
        self.assertEqual(forecast.low, 54.3)
        self.assertEqual(DailyWeatherForecast.objects.count(), 1)


    @patch.object(LocationService, 'get_last_location')
    @patch.object(DarkSkyApiManager, 'get_weekly_forecast')
    def test_get_weekly_forecast(self, get_weekly_forecast, get_last_location):
        class MockLocation:
            latitude = 12
            longitude = 34
        get_last_location.return_value = MockLocation()
        get_weekly_forecast.return_value = [
            {
                'date': date.today(),
                'category': 'clear',
                'high': 98.7,
                'low': 65.4
            }
        ]
        user = User.objects.create(username="test")
        weather_service = WeatherService(user=user)

        forecasts = weather_service.update_forecasts()

        get_last_location.assert_called()
        get_weekly_forecast.assert_called_with(
            latitude=12,
            longitude=34
        )
        self.assertEqual(len(forecasts), 1)
        forecast = DailyWeatherForecast.objects.get(user=user)
        self.assertEqual(forecast.date, date.today())
        self.assertEqual(forecast.category, DailyWeatherForecast.CLEAR)
        self.assertEqual(forecast.high, 98.7)
        self.assertEqual(forecast.low, 65.4)

class ForecastViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test"
        )
        self.client.force_authenticate(self.user)

    def create_weather_forecast(self, date, category=DailyWeatherForecast.CLEAR, high=75, low=57):
        DailyWeatherForecast.objects.create(
            user = self.user,
            date = date,
            category = category,
            high = high,
            low = low
        )

    @patch.object(LocationService, 'get_location_on')
    @patch.object(DarkSkyApiManager, 'get_daily_forecast')
    def test_weather_forecast_does_not_exist(self, get_forecast, get_location_on):
        class MockLocation:
            latitude = 12
            longitude = 34
        get_location_on.return_value = MockLocation()
        get_forecast.return_value = {
            'date': date.today(),
            'category': DailyWeatherForecast.RAIN,
            'high': 67.8,
            'low': 56.7
        }
        
        response = self.client.get(reverse('weather-day', kwargs={
            'day': date.today().strftime('%Y-%m-%d')
        }))

        self.assertEqual(response.status_code, 200)
        get_forecast.assert_called_with(
            date = date.today(),
            latitude = 12,
            longitude = 34
        )
        self.assertEqual(response.data['date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['category'], 'rain')
        self.assertEqual(response.data['high'], 67.8)
        self.assertEqual(response.data['low'], 56.7)

    def test_get_weather_forecast(self):
        self.create_weather_forecast(date=date.today())

        response = self.client.get(reverse('weather-day', kwargs={
            'day': date.today().strftime('%Y-%m-%d')
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['category'], 'clear')
        self.assertEqual(response.data['high'], 75)
        self.assertEqual(response.data['low'], 57)

    def test_get_weather_for_date_range(self):
        for offset in range(14):
            self.create_weather_forecast(
                date = date.today() - timedelta(days=offset),
                high = 80 - offset
            )
        self.user.date_joined = timezone.now() - timedelta(days=15)
        self.user.save()

        response = self.client.get(reverse('weather-range', kwargs={
            'start': (date.today() - timedelta(days=6)).strftime('%Y-%m-%d'),
            'end': date.today().strftime('%Y-%m-%d')
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 7)
        forecast = response.data[-1]
        self.assertEqual(forecast['date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(forecast['high'], 80)

    @patch.object(WeatherService, 'update_forecasts')
    def test_update_forecasts(self, update_forecasts):
        update_forecasts.return_value = [
            DailyWeatherForecast.objects.create(
                user = self.user,
                date = date(2019,6,27),
                category = DailyWeatherForecast.CLEAR,
                high = 78.9,
                low = 45.6
            ), 
            DailyWeatherForecast.objects.create(
                user = self.user,
                date = date(2019,6,28),
                category = DailyWeatherForecast.RAIN,
                high = 67.8,
                low = 54.3
            )
        ]

        response = self.client.get(reverse('weather-update'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        forecast = response.data[1]
        self.assertEqual(forecast['date'], '2019-06-28')
        self.assertEqual(forecast['category'], 'rain')
        self.assertEqual(forecast['high'], 67.8)
        self.assertEqual(forecast['low'], 54.3)
