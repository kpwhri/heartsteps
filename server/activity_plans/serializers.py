from rest_framework import serializers

from activity_types.models import ActivityType

from activity_plans.models import ActivityPlan

class ActivityPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPlan
        fields = ('type', 'vigorous', 'start', 'duration', 'complete')

    type = serializers.SlugRelatedField(
        slug_field='name',
        queryset = ActivityType.objects.filter(user=None).all()
        )


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        return representation
