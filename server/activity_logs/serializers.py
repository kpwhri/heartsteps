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
        representation = super().to_representation(instance)
        representation['id'] = str(instance.uuid)
        return representation

class FitbitDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = FitbitDay
        fields = ('date', 'moderate_minutes', 'vigorous_minutes', 'step_count')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_minutes'] = instance.moderate_minutes + instance.vigorous_minutes*2
        return representation
