from django.db import models
from django.contrib.auth.models import User


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
