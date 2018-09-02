from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from weekly_reflection.models import ReflectionTime


class ReflectionTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReflectionTime
        fields = ('day', 'time')

class ReflectionTimeView(APIView):
    """
    Allows weekly reflection time for a user to be queried or set
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            reflection_time = ReflectionTime.objects.get(user=request.user, active=True)
        except ReflectionTime.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        serialized = ReflectionTimeSerializer(reflection_time)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request):
        serialized = ReflectionTimeSerializer(data=request.data)
        if serialized.is_valid():
            ReflectionTime.objects.filter(user=request.user, active=True).update(active=False)
            ReflectionTime.objects.create(
                user = request.user,
                day = serialized.validated_data['day'],
                time = serialized.validated_data['time']
            )
            return Response(serialized.validated_data, status=status.HTTP_200_OK)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)