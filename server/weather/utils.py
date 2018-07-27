from datetime import datetime
import pytz
import requests

from . models import WeatherForecast

WEATHER_OUTDOOR = "outdoor"  # weather is good enough to go outside
WEATHER_OUTDOOR_SNOW = "outdoor_snow"  # it is currently snowing, and not suitable to go outside
WEATHER_INDOOR = "indoor"  # weather is unfit to go outside and one should stay indoors


class DarkSkyApiManager:
    """
    Hits the DarkSky weather forecast API.
    https://darksky.net/dev/docs
    """
    DARK_SKY_SNOW = "snow"

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
            # fromtimestamp returns local time - switch to UTC
            time=datetime.fromtimestamp(next_hour['time'], tz=pytz.utc),
            precip_probability=next_hour['precipProbability'],
            # precipType does not exist if no precipitation
            precip_type=next_hour.get('precipType', 'None'),
            temperature=next_hour['temperature'],
            apparent_temperature=next_hour['apparentTemperature'],
            wind_speed=next_hour['windSpeed'],
            cloud_cover=next_hour['cloudCover']
        )
        return weather_forecast

        if __name__ == '__main__':
            dk = DarkSkyApiManager()
            dk.get_hour_forecast(47.620506, -122.349277)


class WeatherUtils:

    def get_weather_context(weather_forecast):
        if weather_forecast.precip_probability < 70.0 and weather_forecast.apparent_temperature > 32.0 and weather_forecast.apparent_temperature < 90.0:
            return WEATHER_OUTDOOR
        elif weather_forecast.precip_probability > 0.0 and weather_forecast.precip_type == DARK_SKY_SNOW and weather_forecast.apparent_temperature > 25.0:
            return WEATHER_OUTDOOR_SNOW
        else:
            return WEATHER_INDOOR
