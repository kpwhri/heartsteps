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

    def post(self, request):
        if not isinstance(request.data['flag'], str) or request.data['flag'] == "":
            return Response({"Cannot add flag"}, status.HTTP_400_BAD_REQUEST)
        
        new_flag = request.data['flag']
        current_flags = FeatureFlags.objects.filter(user=request.user).first()
        flags_list = current_flags.flags.split(", ")

        if not new_flag in flags_list:
            updated_flags = current_flags.flags + ", " + new_flag
            current_flags.flags = updated_flags
            current_flags.save()
            return Response({"Successfully added flag"}, status=status.HTTP_201_CREATED)
        return Response({"Flag already exists, flag was not added"}, status.HTTP_202_ACCEPTED)
