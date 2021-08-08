from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

# Create your views here.
from .models import EventLog

class UserLogsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user_logs = EventLog.objects.filter(
            user = request.user
        ).order_by('timestamp') \
        .all()

        if user_logs:
            serialized_user_logs = []
            for user_log in user_logs:
                serialized_user_logs.append({
                    'timestamp': user_log.timestamp,
                    'status': user_log.status
                })
            return Response(serialized_user_logs)
        else:
            return Response('No user logs', status=status.HTTP_404_NOT_FOUND)
