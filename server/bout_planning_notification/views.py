import datetime
from bout_planning_notification.tasks import BoutPlanningFlagException
from feature_flags.models import FeatureFlags
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework import status, permissions
from rest_framework.response import Response

# from weekly_reflection.models import ReflectionTime
from bout_planning_notification.models import FirstBoutPlanningTime, JSONSurvey

from user_event_logs.models import EventLog

from .services import BoutPlanningNotificationService

def get_collapse_subject(prefix):
    return "{}_{}".format(prefix, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))


class FirstBoutPlanningTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstBoutPlanningTime
        fields = ('id','time')

class BoutPlanningSurveyTestView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
                
            user = request.user
        
            if FeatureFlags.exists(user):
                if FeatureFlags.has_flag(user, "bout_planning"):
                    EventLog.log(user, "bout planning shared_task has successfully run", EventLog.INFO)
                    
                    service = BoutPlanningNotificationService(user)
                    
                    json_survey = JSONSurvey.objects.get(name="JustWalk JITAI Daily EMA")
                    survey = json_survey.substantiate(user)
                    # survey = service.create_daily_ema()
                    
                    # message = service.send_notification(title="JustWalk", collapse_subject="bout_planning_survey", survey=survey)
                    message = service.send_notification(title="JustWalk", collapse_subject=get_collapse_subject('dev_front'), survey=survey)
                else:
                    msg = "a user without 'bout_planning' flag came into bout_planning_decision_making: {}=>{}".format(user.username, FeatureFlags.get(user).flags)
                    EventLog.log(user, msg, EventLog.ERROR)
                    raise BoutPlanningFlagException(msg)
            else:
                msg = "a user without any flag came into bout_planning_decision_making: {}".format(user.username)
                EventLog.log(user, msg, EventLog.ERROR)
                raise BoutPlanningFlagException(msg)
            
            return Response(
                    {
                        'notificationId': message.uuid
                    },
                    status = status.HTTP_201_CREATED
                )
        except BoutPlanningNotificationService.NotificationSendError:
            return Response('Unable to send notification', status.HTTP_400_BAD_REQUEST)

        
        # try:
        #     service = BoutPlanningNotificationService(user = request.user)
            
            
            
        #     survey = service.create_test_survey()
            
        #     notification = service.send_notification(survey=survey)
        #     return Response(
        #         {
        #             'notificationId': notification.uuid
        #         },
        #         status = status.HTTP_201_CREATED
        #     )
        # except BoutPlanningNotificationService.NotificationSendError:
        #     return Response('Unable to send notification', status.HTTP_400_BAD_REQUEST)


class FirstBoutPlanningTimeView(APIView):
    """
    Allows weekly reflection time for a user to be queried or set
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response("Not authenticated", status=status.HTTP_UNAUTHORIZED)
        
        if FirstBoutPlanningTime.exists(request.user):
            first_bout_planning_time = FirstBoutPlanningTime.get(user=request.user)
        else:
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
