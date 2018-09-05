from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from activity_plans.serializers import ActivityPlanSerializer, TimeRangeSerializer
from activity_plans.models import ActivityPlan



class ActivityPlansList(APIView):
    """
    Creates activity plans and lists all plans specified in the date range
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serialized = TimeRangeSerializer(data=request.query_params)
        if serialized.is_valid():
            activity_plans = ActivityPlan.objects.filter(
                user=request.user,
                start__range=(
                    serialized.validated_data['start'],
                    serialized.validated_data['end']
                )
            ).all()
            serialized_plans = ActivityPlanSerializer(activity_plans, many=True)
            return Response(serialized_plans.data, status=status.HTTP_200_OK)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serialized = ActivityPlanSerializer(data=request.data)
        if serialized.is_valid():
            activity_plan = ActivityPlan(**serialized.validated_data)
            activity_plan.user = request.user
            activity_plan.save()
            serialzied_plan = ActivityPlanSerializer(activity_plan)
            return Response(serialzied_plan.data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)