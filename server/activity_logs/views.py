from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .serializers import ActivityLogSerializer
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

    def post(self, request):
        serialized = ActivityLogSerializer(data=request.data)
        if serialized.is_valid():
            activity_log = ActivityLog(**serialized.validated_data)
            activity_log.user = request.user
            activity_log.save()
            serialzied_log = ActivityLogSerializer(activity_log)
            return Response(serialzied_log.data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
