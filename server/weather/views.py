from django.core import serializers
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from weather.utils import DarkSkyApiManager
from weather.utils import WeatherUtils
from weather.models import WeatherForecast
from weather.serializers import WeatherForecastSerializer


class WeatherForecastsList(APIView):
    """
    List all weather forecasts or create a new weather forecast.
    """

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
            context = WeatherUtils.get_weather_context(forecast)
            return Response({'id': forecast.id,
                             'context': context},
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
