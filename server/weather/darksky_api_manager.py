from datetime import date
from datetime import datetime
import pytz

from django.utils import timezone
import requests

from locations.services import LocationService

from .models import ServiceRequest
from .models import DailyWeatherForecast

DARK_SKY_API_URL_BASE = 'https://api.darksky.net/forecast/{api_key}/'

class DarkSkyApiManager:
    """
    Hits the DarkSky weather forecast API.
    https://darksky.net/dev/docs
    """

    class RequestFailed(Exception):
        pass

    def __init__(self, user=None):
        self.__user = user
        self.__API_KEY = "f076fa5dc90a5a68a86d075d6f7abab6"

    def make_url(self, latitude, longitude, datetime=None, exclude=[]):
        if datetime:
            url = DARK_SKY_API_URL_BASE + '{latitude},{longitude},{time}'
        else:
            url = DARK_SKY_API_URL_BASE + '{latitude},{longitude}'
        params = [
            'units=us'
        ]
        time = None
        if datetime:
            time = round(datetime.timestamp())
        if len(exclude) > 0:
            params.append('exclude=' + ','.join(exclude))
        url += '?' + '&'.join(params)
        return url.format(
            api_key = self.__API_KEY,
            latitude = latitude,
            longitude = longitude,
            time = time
        )

    def make_request(self, url, name):
        service_request = ServiceRequest.objects.create(
            name = name,
            url = url,
            user = self.__user
        )

        response = requests.get(url)
        if response.status_code is not 200:
            service_request.response_code = response.status_code
            service_request.response_data = response.text
            service_request.response_time = timezone.now()
            service_request.save()
            raise DarkSkyApiManager.RequestFailed('DarkSky request failed')

        service_request.response_code = response.status_code
        service_request.response_data = response.text
        service_request.response_time = timezone.now()
        service_request.save()

        return response.json()

    def get_forecast(self, latitude, longitude, time):
        url = self.make_url(
            latitude = latitude,
            longitude = longitude,
            datetime = time,
            exclude = ['hourly', 'daily', 'alerts', 'minutely', 'flags']
        )
        
        response_data = self.make_request(url, 'DarkSky: get forecast for time')

        forecast = response_data['currently']
        return {
            'latitude': response_data['latitude'],
            'longitude': response_data['longitude'],
            'time': time,
            'precip_probability': forecast.get('precipProbability'),
            'precip_type': forecast.get('precipType', 'None'),
            'temperature': forecast.get('temperature'),
            'apparent_temperature': forecast.get('apparentTemperature'),
            'wind_speed': forecast.get('windSpeed'),
            'cloud_cover': forecast.get('cloudCover')
        }

    def map_icon_to_category(self, icon):
        category_map = {
            'clear-day': DailyWeatherForecast.CLEAR,
            'clear-night': DailyWeatherForecast.CLEAR,
            'rain': DailyWeatherForecast.RAIN,
            'snow': DailyWeatherForecast.SNOW,
            'sleet': DailyWeatherForecast.SNOW,
            'wind': DailyWeatherForecast.WIND,
            'fog': DailyWeatherForecast.CLOUDY,
            'cloudy': DailyWeatherForecast.CLOUDY,
            'partly-cloudy-day': DailyWeatherForecast.PARTIALLY_CLOUDY,
            'partly-cloudy-night': DailyWeatherForecast.PARTIALLY_CLOUDY,
            'hail': DailyWeatherForecast.RAIN,
            'thunderstorm': DailyWeatherForecast.RAIN,
            'tornado': DailyWeatherForecast.RAIN
        }

        if icon in category_map:
            return category_map[icon]
        else:
            return DailyWeatherForecast.PARTIALLY_CLOUDY

    def get_daily_forecast(self, latitude, longitude, date):
        timezone = LocationService.get_timezone_at(
            latitude = latitude,
            longitude = longitude
        )
        dt = datetime(
            date.year,
            date.month,
            date.day,
            tzinfo = timezone
        )
        url = self.make_url(
            latitude = latitude,
            longitude = longitude,
            datetime = dt,
            exclude = ['hourly', 'currently', 'alerts', 'minutely', 'flags']
        )
        response_data = self.make_request(url, 'DarkSky: get weekly forecast')
        tz = pytz.timezone(response_data['timezone'])
        return self.parse_daily_forecast(
            data = response_data['daily']['data'][0],
            timezone = tz
        )


    def get_weekly_forecast(self, latitude, longitude):
        url = self.make_url(
            latitude = latitude,
            longitude = longitude,
            exclude = ['hourly', 'currently', 'alerts', 'minutely', 'flags']
        )
        response_data = self.make_request(url, 'DarkSky: get weekly forecast')
        tz = pytz.timezone(response_data['timezone'])
        forecasts = []
        for forecast in response_data['daily']['data']:
            forecasts.append(
                self.parse_daily_forecast(
                    data = forecast,
                    timezone = tz
                )
            )
        return forecasts

    def parse_daily_forecast(self, data, timezone):
        dt = datetime.fromtimestamp(data['time']).astimezone(timezone)
        day = date(dt.year, dt.month, dt.day)
        category = self.map_icon_to_category(data.get('icon'))
        return {
            'date': day,
            'category': category,
            'high': data.get('temperatureHigh'),
            'low': data.get('temperatureLow')
        }
