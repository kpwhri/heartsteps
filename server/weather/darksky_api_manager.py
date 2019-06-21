from django.utils import timezone
import requests

from .models import ServiceRequest

class DarkSkyApiManager:
    """
    Hits the DarkSky weather forecast API.
    https://darksky.net/dev/docs
    """

    class RequestFailed(Exception):
        pass

    def __init__(self):
        self.API_KEY = "f076fa5dc90a5a68a86d075d6f7abab6"
        self.WEATHER_URL = "https://api.darksky.net/forecast/{api_key}/{latitude},{longitude},{time}?units=us&exclude=hourly,daily,alerts,minutely,flags"

    def get_forecast(self, latitude, longitude, time):
        url = self.WEATHER_URL.format(
            api_key = self.API_KEY,
            latitude = latitude,
            longitude = longitude,
            time = round(time.timestamp())
        )
        
        service_request = ServiceRequest.objects.create(
            name = 'DarkSkyAPI: Get forecast',
            url = url
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

        content = response.json()
        forecast = content['currently']
        return {
            'latitude': content['latitude'],
            'longitude': content['longitude'],
            'time': time,
            'precip_probability': forecast.get('precipProbability'),
            'precip_type': forecast.get('precipType', 'None'),
            'temperature': forecast.get('temperature'),
            'apparent_temperature': forecast.get('apparentTemperature'),
            'wind_speed': forecast.get('windSpeed'),
            'cloud_cover': forecast.get('cloudCover')
        }
