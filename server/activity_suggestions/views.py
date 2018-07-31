from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django_celery_beat.models import PeriodicTasks

from .models import SuggestionTime
from .serializers import SuggestionTimeSerializer

class SuggestionTimeList(APIView):
    """
    Returns or updates a list of a user's suggested intervention times
    """
    def get(self, request):
        serialized_times = SuggestionTimeSerializer({
            'times': SuggestionTime.objects.filter(user = request.user).all()
        })
        return Response(serialized_times.data, status.HTTP_200_OK)

    def post(self, request):
        if 'times' not in request.data:
            return Response('Send times', status.HTTP_400_BAD_REQUEST)

        serialized_times = SuggestionTimeSerializer(data=request.data['times'], many=True)
        if serialized_times.is_valid():
            # its simpler to delete and recreate, rather than update cron tasks
            SuggestionTime.objects.filter(user=request.user).delete()

            for time in serialized_times.validated_data:
                SuggestionTime.objects.create(
                    type = time['type'],
                    hour = time['hour'],
                    minute = time['minute'],
                    user = request.user
                )
            return Response(serialized_times.data, status.HTTP_200_OK)
        return Response(serialized_times.errors, status.HTTP_400_BAD_REQUEST)