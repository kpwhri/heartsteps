from rest_framework import serializers
from weather.models import DailyWeatherForecast
from weather.models import WeatherForecast


class WeatherForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherForecast
        fields = '__all__'

class DailyWeatherForecastSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyWeatherForecast
        fields = ['category', 'date', 'high', 'low']