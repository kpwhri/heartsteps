from rest_framework import serializers
from weather.models import WeatherForecast


class WeatherForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherForecast
        fields = '__all__'