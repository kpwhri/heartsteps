from datetime import datetime
import pytz
import requests

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
        response = requests.get(self.WEATHER_URL.format(
            api_key = self.API_KEY,
            latitude = latitude,
            longitude = longitude,
            time = round(time.timestamp())
        ))
        if response.status_code is not 200:
            raise self.RequestFailed()

        content = response.json()
        forecast = content['currently']
        return {
            'latitude': content['latitude'],
            'longitude': content['longitude'],
            'time': forecast.get('time'),
            'precip_probability': forecast.get('percipProbability'),
            'precip_type': forecast.get('precipType', 'None'),
            'temperature': forecast.get('temperature'),
            'apparent_temperature': forecast.get('apparentTemperature'),
            'wind_speed': forecast.get('windSpeed'),
            'cloud_cover': forecast.get('cloudCover')
        }
