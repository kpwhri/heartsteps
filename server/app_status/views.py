from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

class AppStatusAPIView(APIView):
    def get(self, request):
        if request.user:
            if request.user.is_authenticated:
                return Response('authenticated', status=status.HTTP_200_OK)
            else:
                return Response('not authenticated', status=status.HTTP_200_OK)
        else:
            return Response('not authenticated', status=status.HTTP_200_OK)
        
        