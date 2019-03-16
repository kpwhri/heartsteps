from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from .models import PageView

class PageViewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PageView
        fields = ('uri', 'time')

class PageViewView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serialized = PageViewSerializer(data=request.data, many=True)
        if serialized.is_valid():
            serialized.save(
                user = request.user
            )
            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
