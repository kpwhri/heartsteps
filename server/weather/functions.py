import weather.utils
from weather.models import WeatherForecast


class WeatherFunction:
    """
    Create a new weather forecast & return the context.
    """

    def get_context(latitude, longitude):
        # Lookup forecast using DarkSky API
        dark_sky = weather.utils.DarkSkyApiManager()
        forecast = dark_sky.get_hour_forecast(latitude, longitude)
        forecast.save()
        context = weather.utils.WeatherUtils.get_weather_context(forecast)
        return forecast.id, context
