from rest_framework import serializers

from activity_logs.serializers import ActivitySerializer
from activity_plans.models import ActivityPlan

class ActivityPlanSerializer(ActivitySerializer):
    class Meta:
        model = ActivityPlan
        fields = ('type', 'vigorous', 'start', 'duration', 'complete')


