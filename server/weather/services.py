from django.utils import timezone
from geopy.distance import distance as geopy_distance

from days.services import DayService
from locations.services import LocationService

from .darksky_api_manager import DarkSkyApiManager
from .models import WeatherForecast
from .models import DailyWeatherForecast

class WeatherService:

    class UnknownLocation(RuntimeError):
        pass

    class ForecastUnavailable(RuntimeError):
        pass

    class NoForecast(RuntimeError):
        pass

    WEATHER_OUTDOOR = "outdoor"  # weather is good enough to go outside
    WEATHER_OUTDOOR_SNOW = "outdoor_snow"  # it is currently snowing, and not suitable to go outside
    WEATHER_INDOOR = "indoor"  # weather is unfit to go outside and one should stay indoors

    def __init__(self, user=None):
        self.__user = user
        self._client = DarkSkyApiManager(user = user)

    def make_forecast(latitude, longitude, time=None):
        if not time:
            time = timezone.now()

        dark_sky = DarkSkyApiManager()
        forecast = dark_sky.get_forecast(latitude, longitude, time)
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
        if not forecasts:
            raise WeatherService.NoForecast('No forecast')

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

    def is_forecast_in_past(self, forecast):
        day_service = DayService(user = self.__user)
        end_of_day = day_service.get_end_of_day(forecast.date)
        if end_of_day < timezone.now():
            return True
        else:
            return False

    def is_forecast_location_accurate(self, forecast):
        if not forecast.latitude or not forecast.longitude:
            return False

        location_service = LocationService(user = self.__user)
        current_location = location_service.get_current_location()
        current_coords = (current_location.latitude, current_location.longitude)

        forecast_coords = (forecast.latitude, forecast.longitude)
        distance = geopy_distance(current_coords, forecast_coords)
        if distance.km <= 50:
            return True
        else:
            return False

    def _get_location_on(self, date):
        try:
            location_service = LocationService(user=self.__user)
            return location_service.get_location_on(date)
        except LocationService.UnknownLocation:
            return self._get_home_location()

    def _get_home_location(self):
        try:
            location_service = LocationService(user=self.__user)
            return location_service.get_home_location()
        except LocationService.UnknownLocation:
            raise WeatherService.UnknownLocation('Unknown location')

    def _get_current_location(self):
        try:
            location_service = LocationService(user = self.__user)
            return location_service.get_current_location()
        except LocationService.UnknownLocation:
            return self._get_home_location()

    def _can_update_forecast(self, forecast):
        if self.is_forecast_in_past(forecast):
            return False
        if self.is_forecast_location_accurate(forecast):
            return False
        return True

    def get_forecast(self, date):
        try:
            forecast = DailyWeatherForecast.objects.get(
                user = self.__user,
                date = date
            )
            if self._can_update_forecast(forecast):
                return self.update_daily_forecast(date)
            else:
                return forecast
        except DailyWeatherForecast.DoesNotExist:
           return self.update_daily_forecast(date = date)

    def get_forecasts(self, start, end):
        forecasts = DailyWeatherForecast.objects.filter(
            user = self.__user,
            date__gte=start,
            date__lte=end
        ).all()
        return forecasts

    def update_daily_forecast(self, date):
        try:
            location = self._get_location_on(date)
            forecast = self._client.get_daily_forecast(
                date = date,
                latitude = location.latitude,
                longitude = location.longitude
            )

            daily_forecast, created = DailyWeatherForecast.objects.update_or_create(
                user = self.__user,
                date = date,
                defaults = {
                    'category': forecast['category'],
                    'high': forecast['high'],
                    'low': forecast['low']
                }
            )
            return daily_forecast
        except LocationService.UnknownLocation as e:
            raise WeatherService.UnknownLocation(e)
        except DarkSkyApiManager.RequestFailed:
            raise WeatherService.ForecastUnavailable('Request failed')


    def update_forecasts(self):
        try:
            current_location = self._get_current_location()
            forecasts = []
            for forecast in self._client.get_weekly_forecast(latitude = current_location.latitude, longitude = current_location.longitude):
                daily_forecast, created = DailyWeatherForecast.objects.update_or_create(
                    user = self.__user,
                    date = forecast['date'],
                    defaults = {
                        'category': forecast['category'],
                        'high': forecast['high'],
                        'low': forecast['low']
                    }
                )
                forecasts.append(daily_forecast)
            return forecasts
        except LocationService.UnknownLocation as e:
            raise WeatherService.UnknownLocation(e)
        except DarkSkyApiManager.RequestFailed:
            raise WeatherForecast.ForecastUnavailable('Request failed')

