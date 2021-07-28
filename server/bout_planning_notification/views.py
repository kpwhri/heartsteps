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
        fields = ('time',)

class FirstBoutPlanningTimeView(APIView):
    """
    Allows weekly reflection time for a user to be queried or set
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            first_bout_planning_time = FirstBoutPlanningTime.objects.get(user=request.user, active=True)
        except FirstBoutPlanningTime.DoesNotExist:
            first_bout_planning_time = FirstBoutPlanningTime(user=request.user, active=True, time="07:00")
            first_bout_planning_time.save()
        print(first_bout_planning_time.__dict__)
        
        serialized = FirstBoutPlanningTimeSerializer(first_bout_planning_time)
        if serialized.is_valid():
            return Response(serialized.data, status=status.HTTP_200_OK)
        else:
            return Response("Serialization failed: {}".format(serialized.errors), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        print(request.data)
        serialized = FirstBoutPlanningTimeSerializer(data=request.data)
        if serialized.is_valid():
            FirstBoutPlanningTime.objects.update_or_create(
                user = request.user,
                defaults = {
                    'time': serialized.validated_data['time']
                }
            )
            return Response(serialized.validated_data, status=status.HTTP_200_OK)
        else:
            return Response("Deserialization failed: {}".format(serialized.errors), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
