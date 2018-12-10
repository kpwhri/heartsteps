from rest_framework import serializers

from activity_logs.serializers import ActivitySerializer
from activity_plans.models import ActivityPlan

class ActivityPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPlan
        fields = ('type', 'vigorous', 'start', 'duration', 'complete')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        return representation
