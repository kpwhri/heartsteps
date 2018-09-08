from rest_framework import serializers
from activity_plans.models import ActivityPlan, ActivityLog, ActivityType

class TimeRangeSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()


class ActivityPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPlan
        fields = ('type', 'vigorous', 'start', 'duration')

    type = serializers.SlugRelatedField(
        slug_field='name',
        queryset = ActivityType.objects.filter(user=None).all()
        )

    def to_representation(self, instance):
        return_value = super().to_representation(instance)
        return_value['id'] = str(instance.uuid)
        return return_value

    def to_internal_value(self, data):
        return super(ActivityPlanSerializer, self).to_internal_value(data)

class ActivityLogSerializer(ActivityPlanSerializer):
    class Meta:
        model = ActivityLog
        fields = ('type', 'vigorous', 'start', 'duration', 'enjoyed')
    
    enjoyed = serializers.IntegerField(required=False)
