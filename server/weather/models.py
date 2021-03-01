from django.db import models
from django.contrib.auth.models import User

from service_requests.models import ServiceRequest as ServiceRequestBase

class ServiceRequest(ServiceRequestBase):
    pass

class WeatherForecast(models.Model):
    """
    Represents an hourly weather forecast at a specific location and time
    """

    SNOW = 'snow'

    latitude = models.FloatField()
    longitude = models.FloatField()
    time = models.DateTimeField()

    precip_probability = models.FloatField()
    precip_type = models.CharField(max_length=32)
    temperature = models.FloatField()
    apparent_temperature = models.FloatField()
    wind_speed = models.FloatField(null=True, blank=True)
    cloud_cover = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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

    WEATHER_CHOICES = [
        (CLEAR, 'Clear'),
        (PARTIALLY_CLOUDY, 'Partially Cloudy'),
        (CLOUDY, 'Cloudy'),
        (WIND, 'Wind'),
        (RAIN, 'Rain'),
        (SNOW, 'Snow')
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
