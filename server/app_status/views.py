from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.http.response import Http404

from user_event_logs.models import EventLog

# Create your views here.
class AppStatusAPIView(APIView):
    def get(self, request):
        return Response('authenticated', status=status.HTTP_200_OK)

        # # check to see if the request is allowed (i.e. participant is logged in)
        # if not request.user or request.user.is_anonymous:
        #     # TODO: remove, only for testing purposes
        #     # for now, create an empty featureflag for user "test" and use it
        #     # there is a test code for this logic. (test_get_feature_flags_2)
        #     # if anybody change the logic here, it will make the test failing
        #     test_user, _ = User.objects.get_or_create(username="test")
        #     if FeatureFlags.exists(test_user):
        #         feature_flags = FeatureFlags.get(test_user)
        #     else:
        #         feature_flags = FeatureFlags.create(test_user, "")
        #     serialized = FeatureFlagsSerializer(feature_flags)
        #     return Response(serialized.data, status=status.HTTP_200_OK)
        # # if user has featureflag object
        # if FeatureFlags.exists(request.user):
        #     # return the first object
        #     # TODO: replace first() to get(). Because, it is controlled by unique user
        #     feature_flags = FeatureFlags.get(request.user)
        # else:
        #     # if not, create a blank one and return it
        #     feature_flags = FeatureFlags.create(user=request.user)
        # # serialize featureflags                    
        # serialized = FeatureFlagsSerializer(feature_flags)
        # # return serialized featureflags with 200
        # return Response(serialized.data, status=status.HTTP_200_OK)