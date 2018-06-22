"""
Hits the DarkSky weather forecast API.
https://darksky.net/dev/docs
"""
import datetime
import requests
from models.weather_forecast import *


class DarkSkyApiManager:
    def __init__(self):
        self.API_KEY = "f076fa5dc90a5a68a86d075d6f7abab6"
        self.WEATHER_URL = ("https://api.darksky.net/forecast/"
                            "[api_key]/[latitude],[longitude]?units=us"
                            "&exclude=currently,minutely,daily,alerts,flags")

    def get_hour_forecast(self, latitude, longitude):
        """
        This function gets hourly weather forecast for the specified lat/long

        REQUIRES:   dark_sky_api_key = string
                    state = string (short form)
                    city = string
        MODIFIES:   nothing
        EFFECTS:    returns a DataBlock of hourly weather
        """
        request_url = self.WEATHER_URL.replace("[api_key]", self.API_KEY)
        request_url = request_url.replace("[latitude]", str(latitude))
        request_url = request_url.replace("[longitude]", str(longitude))
        response = requests.get(request_url)
        content = response.json()

        response_latitude = content["latitude"]
        response_longitude = content["longitude"]
        # Forecast for current hour is [0], following hour is [1]
        next_hour = content['hourly']['data'][1]
        weather_forecast = WeatherForecast(
            latitude=response_latitude,
            longitude=response_longitude,
            time=datetime.datetime.fromtimestamp(next_hour['time']),
            precip_probability=next_hour['precipProbability'],
            # precipType does not exist if no precipitation
            precip_type=next_hour.get('precipType', 'None'),
            temperature=next_hour['temperature'],
            apparent_temperature=next_hour['apparentTemperature'],
            wind_speed=next_hour['windSpeed'],
            cloud_cover=next_hour['cloudCover'],
            server_created_dtm=datetime.datetime.now()
        )
        weather_forecast.save()
        # Likely we'll want to characterize the weather here
        # and return only the necessary context.
        # Maybe implement as a local function.

        if __name__ = '__main__':
            dk = DarkSkyApiManager()
            dk.get_hour_forecast(47.620506, -122.349277)