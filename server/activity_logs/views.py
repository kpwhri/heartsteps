from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from activity_logs.serializers import ActivityLogSerializer, TimeRangeSerializer
from activity_plans.models import ActivityLog

class ActivityLogsList(APIView):
    """
    Manages activity logs
    """
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serialized = ActivityLogSerializer(data=request.data)
        if serialized.is_valid():
            activity_log = ActivityLog(**serialized.validated_data)
            activity_log.user = request.user
            activity_log.save()
            serialized_log = ActivityLogSerializer(activity_log)
            return Response(serialized_log.data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)