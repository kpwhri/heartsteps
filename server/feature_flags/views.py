from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.http.response import Http404

from .serializers import FeatureFlagsSerializer
from .models import FeatureFlags, User

from user_event_logs.models import EventLog

class FeatureFlagsList(APIView):
    # TODO: re-enable, only for testing purposes
    # permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # check to see if the request is allowed (i.e. participant is logged in)
        if not request.user or request.user.is_anonymous:
            # TODO: remove, only for testing purposes
            # for now, create an empty featureflag for user "test" and use it
            # there is a test code for this logic. (test_get_feature_flags_2)
            # if anybody change the logic here, it will make the test failing
            test_user, _ = User.objects.get_or_create(username="test")
            if FeatureFlags.exists(test_user):
                feature_flags = FeatureFlags.get(test_user)
            else:
                feature_flags = FeatureFlags.create(test_user, "")
            serialized = FeatureFlagsSerializer(feature_flags)
            return Response(serialized.data, status=status.HTTP_200_OK)
        # if user has featureflag object
        if FeatureFlags.exists(request.user):
            # return the first object
            # TODO: replace first() to get(). Because, it is controlled by unique user
            feature_flags = FeatureFlags.get(request.user)
        else:
            # if not, create a blank one and return it
            feature_flags = FeatureFlags.create(user=request.user)
        # serialize featureflags                    
        serialized = FeatureFlagsSerializer(feature_flags)
        # return serialized featureflags with 200
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request):
        add_op = False
        remove_op = False

        # checking invariants
        if "add_flag" in request.data:
            if not isinstance(request.data["add_flag"], str) or request.data["add_flag"] == "":
                return Response({"Cannot add flag"}, status.HTTP_400_BAD_REQUEST)
            add_op = True
        if "remove_flag" in request.data:
            if not isinstance(request.data["remove_flag"], str) or request.data["remove_flag"] == "":
                return Response({"Cannot add flag"}, status.HTTP_400_BAD_REQUEST)
            remove_op = True

        current_flags = FeatureFlags.get(request.user)
        flags_list = current_flags.flags.split(", ")

        # we are adding a flag
        if add_op:
            new_flag = request.data["add_flag"]

            if not new_flag in flags_list:
                updated_flags = current_flags.flags + ", " + new_flag
                current_flags.flags = updated_flags
                current_flags.save()
                return Response({"Successfully added flag"}, status=status.HTTP_201_CREATED)
            return Response({"Flag already exists, flag was not added"}, status.HTTP_202_ACCEPTED)

        # we are removing a flag
        if remove_op:
            remove_flag = request.data["remove_flag"]

            if not remove_flag in flags_list:
                return Response({"Cannot remove flag that does not exist"}, status.HTTP_202_ACCEPTED)

            new_flag_str = ""
            last_flag = flags_list[-1]
            for flag in flags_list:
                if flag != remove_flag:
                    # if this is the last flag in the list, don't add trailing comma
                    if flag == last_flag:
                        new_flag_str += flag
                    else:
                        new_flag_str += flag + ", "

            # if remove_flag is last flag in list
            if remove_flag == last_flag:
                # get rid of trailing comma
                new_flag_str = new_flag_str[:-2]

            current_flags.flags = new_flag_str
            current_flags.save()
            return Response({"Successfully removed flag"}, status=status.HTTP_200_OK)
