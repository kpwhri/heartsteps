from datetime import date
from datetime import datetime

from django.utils import timezone
import requests

from days.services import DayService

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

    def make_url(self, latitude, longitude, time=None, exclude=[]):
        if time:
            url = DARK_SKY_API_URL_BASE + '{latitude},{longitude},{time}'
        else:
            url = DARK_SKY_API_URL_BASE + '{latitude},{longitude}'
        params = [
            'units=us'
        ]
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
            raise self.RequestFailed()

        service_request.response_code = response.status_code
        service_request.response_data = response.text
        service_request.response_time = timezone.now()
        service_request.save()

        return response.json()

    def get_forecast(self, latitude, longitude, time):
        url = self.make_url(
            latitude = latitude,
            longitude = longitude,
            time = round(time.timestamp()),
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

    def get_weekly_forecast(self, latitude, longitude):
        url = self.make_url(
            latitude = latitude,
            longitude = longitude,
            exclude = ['hourly', 'currently', 'alerts', 'minutely', 'flags']
        )

        response_data = self.make_request(url, 'DarkSky: get weekly forecast')

        forecasts = []
        for forecast in response_data['daily']:
            dt = datetime.fromtimestamp(forecast['time'])
            day = date(dt.year, dt.month, dt.day)
            if self.__user:
                day_service = DayService(user = self.__user)
                day = day_service.get_date_at(dt)
            category = self.map_icon_to_category(forecast.get('icon'))
            forecasts.append({
                'date': day,
                'category': category,
                'high': forecast.get('temperatureHigh'),
                'low': forecast.get('temperatureLow')
            })
        return forecasts
