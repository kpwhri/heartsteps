from django.core import serializers
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from weather.dark_sky import DarkSkyApiManager
from weather.models import WeatherForecast
from weather.serializers import WeatherForecastSerializer


class WeatherForecastsList(APIView):
    """
    List all weather forecasts or create a new weather forecast.
    """
    WEATHER_OUTDOOR = "outdoor" # weather is good enough to go outside
    WEATHER_OUTDOOR_SNOW = "outdoor_snow" # it is currently snowing, and not suitable to go outside
    WEATHER_INDOOR = "indoor" # weather is unfit to go outside and one should stay indoors

    def _get_weather_context(self, weather_forecast):
        if weather_forecast.precip_probability < 70.0 and weather_forecast.apparent_temperature > 32.0 and weather_forecast.apparent_temperature < 90.0:
            return self.WEATHER_OUTDOOR
        elif weather_forecast.precip_probability > 0.0 and weather_forecast.precip_type == DARK_SKY_SNOW and weather_forecast.apparent_temperature > 25.0:
            return self.WEATHER_OUTDOOR_SNOW
        else:
            return self.WEATHER_INDOOR

    def get(self, request, format=None):
        forecasts = WeatherForecast.objects.all()
        serializer = WeatherForecastSerializer(forecasts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        if latitude and longitude:
            # Lookup forecast using DarkSky API
            dark_sky = DarkSkyApiManager()
            forecast = dark_sky.get_hour_forecast(latitude, longitude)
            forecast.save()
            return Response({ 'id': forecast.id,
                              'context': self._get_weather_context(forecast) },
                              status=status.HTTP_201_CREATED)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


class WeatherForecastsDetail(APIView):
    """
    Retrieve, update or delete a weather forecast.
    """

    def _get_object(self, pk):
        try:
            return WeatherForecast.objects.get(pk=pk)
        except WeatherForecast.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        forecast = self._get_object(pk)
        serializer = WeatherForecastSerializer(forecast)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        forecast = self._get_object(pk)
        serializer = WeatherForecastSerializer(forecast, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        forecast = self._get_object(pk)
        forecast.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
