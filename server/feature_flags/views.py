from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.http.response import Http404

from .serializers import FeatureFlagsSerializer
from .models import FeatureFlags

class FeatureFlagsList(APIView):
    # TODO: re-enable, only for testing purposes
    # permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # check to see if the request is allowed (i.e. participant is logged in)
        if not request.user or request.user.is_anonymous:
            # TODO: remove, only for testing purposes
            feature_flags = FeatureFlags.objects.filter(user__username='test').first()
            serialized = FeatureFlagsSerializer(feature_flags)
            return Response(serialized.data, status=status.HTTP_200_OK)
            return Response({"No participant, please log in"}, status.HTTP_400_BAD_REQUEST)

        feature_flags = FeatureFlags.objects.filter(user=request.user).first()

        if not feature_flags or feature_flags == []:
            return Response({"No feature flags object for user"}, status.HTTP_400_BAD_REQUEST)

        serialized = FeatureFlagsSerializer(feature_flags)
        return Response(serialized.data, status=status.HTTP_200_OK)
