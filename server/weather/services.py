from weather.darksky_api_manager import DarkSkyApiManager
from weather.models import WeatherForecast

class WeatherService:

    WEATHER_OUTDOOR = "outdoor"  # weather is good enough to go outside
    WEATHER_OUTDOOR_SNOW = "outdoor_snow"  # it is currently snowing, and not suitable to go outside
    WEATHER_INDOOR = "indoor"  # weather is unfit to go outside and one should stay indoors

    def make_forecast(latitude, longitude):
        dark_sky = DarkSkyApiManager
        forecast = dark_sky.get_hour_forecast(latitude, longitude)
        return WeatherForecast.objects.create(**forecast)

    def get_context(temperature, precipitation_probability, precipitation_type):
        if precipitation_probability > 0.0 and precipitation_type == WeatherForecast.SNOW and temperature > 25.0:
            return WeatherService.WEATHER_OUTDOOR_SNOW
        elif precipitation_probability < 70.0 and temperature > 32.0 and temperature < 90.0:
            return WeatherService.WEATHER_OUTDOOR
        else:
            return WeatherService.WEATHER_INDOOR

    def get_forecast_context(weather_forecast):
        return WeatherService.get_context(
            temperature = weather_forecast.apparent_temperature,
            precipitation_probability = weather_forecast.precip_probability,
            precipitation_type = weather_forecast.precip_type
        )

    def get_average_forecast_context(forecasts):
        """
        From a list of weather forecasts, make an average and return it's context
        """
        average_temperature = sum([forecast.apparent_temperature for forecast in forecasts])/len(forecasts)
        average_precipitation_probability = sum([forecast.precip_probability for forecast in forecasts])/len(forecasts)

        if WeatherForecast.SNOW in [forecast.precip_type for forecast in forecasts]:
            worst_precipitation_type = WeatherForecast.SNOW
        else:
            worst_precipitation_type = forecasts[0].precip_type

        return WeatherService.get_context(
            temperature = average_temperature,
            precipitation_probability = average_precipitation_probability,
            precipitation_type = worst_precipitation_type
        )
