from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

# from weekly_reflection.models import ReflectionTime
from bout_planning_notification.models import FirstBoutPlanningTime

class FirstBoutPlanningTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstBoutPlanningTime
        fields = ('id','time')


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
            first_bout_planning_time = FirstBoutPlanningTime.create(user=request.user)
        
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
