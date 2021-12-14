from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework import status, permissions
from rest_framework.response import Response

# from weekly_reflection.models import ReflectionTime
from bout_planning_notification.models import FirstBoutPlanningTime

from user_event_logs.models import EventLog

from .services import BoutPlanningNotificationService


class FirstBoutPlanningTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstBoutPlanningTime
        fields = ('id','time')

class BoutPlanningSurveyTestView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            service = BoutPlanningNotificationService(user = request.user)
            survey = service.create_test_survey()
            notification = service.send_notification(survey=survey)
            return Response(
                {
                    'notificationId': notification.uuid
                },
                status = status.HTTP_201_CREATED
            )
        except BoutPlanningNotificationService.NotificationSendError:
            return Response('Unable to send notification', status.HTTP_400_BAD_REQUEST)


class FirstBoutPlanningTimeView(APIView):
    """
    Allows weekly reflection time for a user to be queried or set
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response("Not authenticated", status=status.HTTP_UNAUTHORIZED)
        
        if FirstBoutPlanningTime.exists(request.user):
            EventLog.debug(request.user, "FirstBoutPlanningTime exists")
            first_bout_planning_time = FirstBoutPlanningTime.get(user=request.user)
        else:
            EventLog.debug(request.user, "FirstBoutPlanningTime does not exist")
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serialized = FirstBoutPlanningTimeSerializer(first_bout_planning_time)
        
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response("Not authenticated", status=status.HTTP_UNAUTHORIZED)
        
        time = request.data['time']
        
        if FirstBoutPlanningTime.exists(request.user):
            first_bout_planning_time = FirstBoutPlanningTime.update(user=request.user, time=time)
        else:
            first_bout_planning_time = FirstBoutPlanningTime.create(user=request.user, time=time)
        
        serialized = FirstBoutPlanningTimeSerializer(first_bout_planning_time)
        
        return Response(serialized.data, status=status.HTTP_200_OK)
