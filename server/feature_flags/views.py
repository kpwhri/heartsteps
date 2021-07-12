from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .serializers import FeatureFlagsSerializer
from .models import FeatureFlags

class FeatureFlagsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_feature_flags(self):
        return []

    def get(self, request):
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
