from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .serializers import ActivityLogSerializer, TimeRangeSerializer
from .models import ActivityLog, ActivityType

class ActivityLogsDetail(APIView):
    permissions_classes = (permissions.IsAuthenticated,)

    def get_activity(self, user, log_id):
        try:
            return ActivityLog.objects.get(
                user = user,
                uuid = log_id
            )
        except:
            raise Http404()
    
    def get(self, request, log_id):
        activity_log = self.get_activity(request.user, log_id)
        serialized = ActivityLogSerializer(activity_log)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, log_id):
        activity_log = self.get_activity(request.user, log_id)
        serialized = ActivityLogSerializer(activity_log, data=request.data)
        if serialized.is_valid():
            serialized.save()
            return Response(serialized.data, status=status.HTTP_200_OK)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, log_id):
        activity_log = self.get_activity(request.user, log_id)
        activity_log.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ActivityLogsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serialized = TimeRangeSerializer(data=request.query_params)
        if serialized.is_valid():
            activity_logs = ActivityLog.objects.filter(
                user = request.user,
                start__range=(
                    serialized.validated_data['start'],
                    serialized.validated_data['end']
                )
            ).all()
            serialized_logs = ActivityLogSerializer(activity_logs, many=True)
            return Response(serialized_logs.data, status = status.HTTP_200_OK)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serialized = ActivityLogSerializer(data=request.data)
        if serialized.is_valid():
            serialized.save(user=request.user)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
