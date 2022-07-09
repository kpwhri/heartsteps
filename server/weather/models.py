from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from service_requests.models import ServiceRequest as ServiceRequestBase

class ZipCodeInfo(models.Model):
    user = models.ForeignKey(User, null=False, on_delete = models.CASCADE)
    app_key = models.CharField(max_length=255, null=False)

    # who put the zip code
    # the user in the zip code
    # when the input was conducted
    # what the zip code is
    # what the fetched lat/lon are

class ServiceRequest(ServiceRequestBase):
    pass

class WeatherForecast(models.Model):
    """
    Represents an hourly weather forecast at a specific location and time
    """

    # {
    #     'latitude': response_data['latitude'],
    #     'longitude': response_data['longitude'],
    #     'time': time,
    #     'precip_probability': forecast.get('precipProbability'),
    #     'precip_type': forecast.get('precipType', 'None'),
    #     'temperature': forecast.get('temperature'),
    #     'apparent_temperature': forecast.get('apparentTemperature'),
    #     'wind_speed': forecast.get('windSpeed'),
    #     'cloud_cover': forecast.get('cloudCover')
    # }

    SNOW = 'snow'

    precip_probability = models.FloatField()
    precip_type = models.CharField(max_length=32)
    temperature = models.FloatField()
    apparent_temperature = models.FloatField()
    wind_speed = models.FloatField(null=True, blank=True)
    cloud_cover = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    time = models.DateTimeField(null=True)
    

    @property
    def temperature_celcius(self):
        return (self.temperature - 32)/1.8

    def __str__(self):
        return "Apparent temp is %s at (%s, %s)" % (self.apparent_temperature, self.latitude, self.longitude)


class DailyWeatherForecast(models.Model):

    CLEAR = 'clear'
    PARTIALLY_CLOUDY = 'partially-cloudy'
    CLOUDY = 'cloudy'
    WIND = 'wind'
    RAIN = 'rain'
    SNOW = 'snow'
    UNKNOWN = 'unknown'

    WEATHER_CHOICES = [
        (CLEAR, 'Clear'),
        (PARTIALLY_CLOUDY, 'Partially Cloudy'),
        (CLOUDY, 'Cloudy'),
        (WIND, 'Wind'),
        (RAIN, 'Rain'),
        (SNOW, 'Snow'),
        (UNKNOWN, 'Unknown')
    ]

    user = models.ForeignKey(User, on_delete = models.CASCADE)
    date = models.DateField()

    category = models.CharField(max_length=70, choices=WEATHER_CHOICES)
    high = models.FloatField()
    low = models.FloatField()

    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        unique_together = ['user', 'date']

    def __str__(self):
        return "%s: %s" % (self.user.username, self.date.strftime('%Y-%m-%d'))
