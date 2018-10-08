from weather.utils import DarkSkyApiManager
from weather.models import WeatherForecast

class WeatherService:

    WEATHER_OUTDOOR = "outdoor"  # weather is good enough to go outside
    WEATHER_OUTDOOR_SNOW = "outdoor_snow"  # it is currently snowing, and not suitable to go outside
    WEATHER_INDOOR = "indoor"  # weather is unfit to go outside and one should stay indoors

    def make_forecast(latitude, longitude):
        dark_sky = DarkSkyApiManager
        forecast = dark_sky.get_hour_forecast(latitude, longitude)
        forecast.save()
        return forecast

    def get_forecast_context(weather_forecast):
        if weather_forecast.precip_probability < 70.0 and weather_forecast.apparent_temperature > 32.0 and weather_forecast.apparent_temperature < 90.0:
            return self.WEATHER_OUTDOOR
        elif weather_forecast.precip_probability > 0.0 and weather_forecast.precip_type == 'snow' and weather_forecast.apparent_temperature > 25.0:
            return self.WEATHER_OUTDOOR_SNOW
        else:
            return self.WEATHER_INDOOR

    def get_average_forecast_context(forecasts):
        """
        From a list of weather forecasts, make an average and return it's context
        """
        return False
