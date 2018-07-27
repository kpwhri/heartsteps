from django.db import models
from django.contrib.auth.models import User


class WeatherForecast(models.Model):
    """
    Represents an hourly weather forecast
    currently using the DarkSky API
    """
    latitude = models.FloatField()
    longitude = models.FloatField()
    time = models.DateTimeField()
    precip_probability = models.FloatField()
    precip_type = models.CharField(max_length=32)
    temperature = models.FloatField()
    apparent_temperature = models.FloatField()
    wind_speed = models.FloatField()
    cloud_cover = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Apparent temp is %s at (%s, %s)" % (self.apparent_temperature, self.latitude, self.longitude)
