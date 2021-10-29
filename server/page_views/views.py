from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from user_event_logs.models import EventLog

from .models import PageView

class PageViewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PageView
        fields = ('uri', 'time', 'platform', 'version', 'build')

class PageViewView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if type(request.data) is list:
            serialized = PageViewSerializer(data=request.data, many=True)
        else:
            serialized = PageViewSerializer(data=request.data)
        if serialized.is_valid():
            serialized.save(
                user = request.user
            )
            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

