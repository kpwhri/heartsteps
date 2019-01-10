import pytz
from datetime import datetime

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from .models import StepCount
from .tasks import start_decision


class StepCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepCount
        fields = ('step_number', 'step_dtm')

    def to_internal_value(self, data):
        """ Convert Unix timestamp to date """
        data['step_dtm'] = datetime.utcfromtimestamp(data['step_dtm']/1000).astimezone(pytz.UTC)
        return data


class StepCountUpdateView(APIView):
    """
    Save step count from Fitbit watch
    """

    def post(self, request):
        serialized = StepCountSerializer(data=request.data)
        if serialized.is_valid():
            step_count = StepCount(**serialized.validated_data)
            step_count.user = request.user
            step_count.save()
            start_decision.apply_async(kwargs={
                'step_count_id': step_count.id
            })
            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
