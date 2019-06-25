from django.core import serializers
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from days.views import DayView
from weather.models import DailyWeatherForecast
from weather.serializers import DailyWeatherForecastSerializer

class DailyWeatherView(DayView):

    def get(self, request, day):
        day = self.parse_date(day)
        self.validate_date(request.user, day)
        try:
            weather_forcast = DailyWeatherForecast.objects.get(
                user = request.user,
                date = day
            )
        except DailyWeatherForecast.DoesNotExist:
            return Response('Not found', status=status.HTTP_404_NOT_FOUND)
        serialized = DailyWeatherForecastSerializer(weather_forcast)
        return Response(serialized.data)

class DailyWeatherRangeView(DayView):

    def get(self, request, start, end):
        start_date = self.parse_date(start)
        end_date = self.parse_date(end)
        day_joined = self.get_day_joined(request.user)

        if start_date < day_joined:
            start_date = day_joined
        if end_date < day_joined:
            raise Http404()

        if start_date > end_date:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        results = DailyWeatherForecast.objects.filter(
            user = request.user,
            date__range=[start_date, end_date]
        ).all()
        serialized = DailyWeatherForecastSerializer(results, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
