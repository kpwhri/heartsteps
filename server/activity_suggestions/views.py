from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django_celery_beat.models import PeriodicTasks

from .models import SuggestionTime, Configuration
from .serializers import SuggestionTimeSerializer

class SuggestionTimeList(APIView):
    """
    Returns or updates a list of a user's suggested intervention times
    """
    def get(self, request):
        try:
            configuration = Configuration.objects.get(user=request.user)
        except Configuration.DoesNotExist:
            return Response('', status.HTTP_404_NOT_FOUND)
        return Response(
            SuggestionTimeSerializer(configuration).data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        try:
            configuration = Configuration.objects.get(user=request.user)
        except Configuration.DoesNotExist:
            return Response('', status.HTTP_404_NOT_FOUND)
        serialized_times = SuggestionTimeSerializer(data=request.data)
        if serialized_times.is_valid():
            for category in serialized_times.validated_data:
                SuggestionTime.objects.update_or_create(
                    user = request.user,
                    category = category,
                    defaults = serialized_times.validated_data[category]
                )
            return Response(request.data, status.HTTP_200_OK)
        return Response(serialized_times.errors, status.HTTP_400_BAD_REQUEST)