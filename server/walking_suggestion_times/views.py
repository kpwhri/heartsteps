from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from django_celery_beat.models import PeriodicTasks

from .models import SuggestionTime, User
from .serializers import SuggestionTimeSerializer
from .signals import suggestion_times_updated

class SuggestionTimeList(APIView):
    """
    Returns or updates a list of a user's suggested intervention times
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        suggestion_times = list(SuggestionTime.objects.filter(user=request.user).all())

        if len(suggestion_times) > 0:
            return_value = {}
            for suggestion_time in suggestion_times:
                time = "%s:%s" % (suggestion_time.hour, suggestion_time.minute)
                return_value[suggestion_time.category] = time
            return Response(return_value, status=status.HTTP_200_OK)
        else:
            return Response('None', status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serialized_times = SuggestionTimeSerializer(data=request.data)
        if serialized_times.is_valid():
            for category in serialized_times.validated_data:
                SuggestionTime.objects.update_or_create(
                    user = request.user,
                    category = category,
                    defaults = serialized_times.validated_data[category]
                )
            suggestion_times_updated.send(User, username=request.user.username)
            return Response(request.data, status.HTTP_200_OK)
        return Response(serialized_times.errors, status.HTTP_400_BAD_REQUEST)
