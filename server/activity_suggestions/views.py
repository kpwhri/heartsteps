from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django_celery_beat.models import PeriodicTasks

from .models import SuggestionTime, SuggestionTimeConfiguration
from .serializers import SuggestionTimeConfigurationSerializer

class SuggestionTimeList(APIView):
    """
    Returns or updates a list of a user's suggested intervention times
    """
    def get(self, request):
        try:
            configuration = SuggestionTimeConfiguration.objects.get(user=request.user)
        except SuggestionTimeConfiguration.DoesNotExist:
            return Response('', status.HTTP_404_NOT_FOUND)
        return Response(
            SuggestionTimeConfigurationSerializer(configuration).data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        try:
            configuration = SuggestionTimeConfiguration.objects.get(user=request.user)
        except SuggestionTimeConfiguration.DoesNotExist:
            return Response('', status.HTTP_404_NOT_FOUND)
        serialized_configuration = SuggestionTimeConfigurationSerializer(data=request.data)
        if serialized_configuration.is_valid():
            for time_category in serialized_configuration.validated_data:
                time = serialized_configuration.validated_data[time_category]
                SuggestionTime.objects.create(
                    configuration = configuration,
                    type = time_category,
                    hour = time['hour'],
                    minute = time['minute']
                )
            return Response(request.data, status.HTTP_200_OK)
        return Response(serialized_configuration.errors, status.HTTP_400_BAD_REQUEST)