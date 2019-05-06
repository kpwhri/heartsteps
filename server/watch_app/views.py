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

