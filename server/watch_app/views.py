import pytz
from datetime import datetime

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from participants.views import LoginView as ParticipantLoginView

from .models import StepCount, WatchInstall, User
from .signals import step_count_updated

class StepCountUpdateView(APIView):
    """
    Save step count from Fitbit watch
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if 'step_number' in request.data and isinstance(request.data['step_number'], list):
            start_time = None
            step_counts = []
            for steps in request.data['step_number']:
                time = datetime.utcfromtimestamp(steps['time']/1000).astimezone(pytz.UTC)
                if start_time:
                    step_counts.append({
                        'start': start_time,
                        'end': time,
                        'steps': steps['steps']
                    })
                    start_time = time
                else:
                    start_time = time
            for step_count in step_counts:
                StepCount.objects.update_or_create(
                    user = request.user,
                    start = step_count['start'],
                    end = step_count['end'],
                    defaults = {
                        'steps': step_count['steps']
                    }
                )
            step_count_updated.send(User, username=request.user.username)
            return Response('', status=status.HTTP_201_CREATED)
        return Response('step_number not included', status=status.HTTP_400_BAD_REQUEST)

class LoginView(ParticipantLoginView):

    def authentication_successful(self):
        install, _ = WatchInstall.objects.update_or_create(user = self.participant.user)


class WatchAppStatus(object):
    def __init__(self, installed, lastUpdated):
        self.installed = installed
        self.lastUpdated = lastUpdated

class WatchAppStatusSerializer(serializers.Serializer):
    installed = serializers.DateTimeField()
    lastUpdated = serializers.DateTimeField()

class WatchAppStatusView(APIView):
    """
    Return the current status of the user's watch app
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):

        installed = False
        lastUpdated = None

        try:
            watch_install = WatchInstall.objects.get(user=request.user)
            installed = watch_install.updated
        except WatchInstall.DoesNotExist:
            pass

        last_step_count = StepCount.objects.filter(user = request.user).last()
        if last_step_count:
            lastUpdated = last_step_count.end

        serializer = WatchAppStatusSerializer(
            WatchAppStatus(
                installed = installed,
                lastUpdated = lastUpdated
            )
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

