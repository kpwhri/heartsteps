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
            feature_flags = FeatureFlags.objects.filter(user__username="test").first()
            serialized = FeatureFlagsSerializer(feature_flags)
            return Response(serialized.data, status=status.HTTP_200_OK)
            return Response({"No participant, please log in"}, status.HTTP_400_BAD_REQUEST)

        feature_flags = FeatureFlags.objects.filter(user=request.user).first()

        if not feature_flags or feature_flags == []:
            return Response({"No feature flags object for user"}, status.HTTP_400_BAD_REQUEST)

        serialized = FeatureFlagsSerializer(feature_flags)
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

        current_flags = FeatureFlags.objects.filter(user=request.user).first()
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
