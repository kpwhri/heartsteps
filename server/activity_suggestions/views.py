from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .models import SuggestionTime, TIMES
from .serializers import SuggestionTimeSerializer

class SuggestionTimeList(APIView):
    """
    Returns or updates a list of a user's suggested intervention times
    """

    def post(self, request):
        for key in request.data:
            if key not in TIMES:
                return Response("Unexpeted key", status=status.HTTP_400_BAD_REQUEST) 

        suggestion_times = {}
        for time in TIMES:
            if time in request.data:
                suggested_time = self.create_or_update_time(
                    time,
                    request.data[time],
                    request.user
                )
                if not suggested_time:
                    return Response(
                        "Incorrect format for %s" % (time),
                        status=status.HTTP_400_BAD_REQUEST
                        ) 
                suggestion_times[time] = suggested_time.time_of_day
        return Response(suggestion_times, status.HTTP_200_OK)

    def create_or_update_time(self, type, time_of_day, user):
        time_serialized = SuggestionTimeSerializer(data={
            'type': type,
            'time_of_day': time_of_day
        })

        if not time_serialized.is_valid():
            return False

        try:
            time = SuggestionTime.objects.get(
                user = user,
                type = type
            )

        except SuggestionTime.DoesNotExist:
            time = SuggestionTime(
                user = user,
                type = type
            )

        time.time_of_day = time_serialized.validated_data['time_of_day']
        time.save()
        return time
