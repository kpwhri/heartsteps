from rest_framework import serializers

from activity_logs.serializers import ActivityLogSerializer

from activity_plans.models import ActivityPlan

class ActivityPlanSerializer(ActivityLogSerializer):
    class Meta:
        model = ActivityPlan
        fields = ('type', 'vigorous', 'start', 'duration', 'complete')

    complete = serializers.BooleanField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['complete'] = instance.complete
        return representation

    def save(self, **kwargs):
        complete = self.validated_data['complete']
        del self.validated_data['complete']

        activity_plan = super().save(**kwargs)
        if complete:
            activity_plan.update_activity_log()
        else:
            activity_plan.remove_activity_log()
        return activity_plan

