from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from activity_logs.serializers import TimeRangeSerializer

from activity_plans.serializers import ActivityPlanSerializer
from activity_plans.models import ActivityPlan

class ActivityPlanSummaryView(APIView):

    def get(self, request):
        activity_types = {}
        for plan in ActivityPlan.objects.filter(user=request.user):
            activity_type_name = plan.type.name
            if activity_type_name not in activity_types:
                activity_types[activity_type_name] = 1
            else:
                activity_types[activity_type_name] += 1
        return Response({
            'activityTypes': activity_types
        })

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
            serialized.save(user=request.user)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivityPlanView(APIView):

    def get_plan(self, user, plan_id):
        try:
            return ActivityPlan.objects.get(
                user = user,
                uuid = plan_id
            )
        except ActivityPlan.DoesNotExist:
            raise Http404

    def get(self, request, plan_id):
        plan = self.get_plan(request.user, plan_id)
        serialized = ActivityPlanSerializer(plan)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, plan_id):
        plan = self.get_plan(request.user, plan_id)
        serialized = ActivityPlanSerializer(plan, data=request.data)
        if serialized.is_valid():
            serialized.save()
            return Response(serialized.data, status=status.HTTP_200_OK)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, plan_id):
        plan = self.get_plan(request.user, plan_id)
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    