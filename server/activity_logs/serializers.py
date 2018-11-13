from rest_framework import serializers

from fitbit_api.models import FitbitDay

from .models import AbstractActivity, ActivityType

class TimeRangeSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractActivity
        fields = ('type', 'vigorous', 'start', 'duration')

    type = serializers.SlugRelatedField(
        slug_field='name',
        queryset = ActivityType.objects.filter(user=None).all()
        )

    def to_representation(self, instance):
        return_value = super().to_representation(instance)
        return_value['id'] = str(instance.uuid)
        return return_value

class FitbitDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = FitbitDay
        fields = ('date', 'active_minutes', 'total_steps')
