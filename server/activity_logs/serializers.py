from rest_framework import serializers

from fitbit_api.models import FitbitDay, FitbitActivity

from activity_logs.models import ActivityLog, ActivityType

class TimeRangeSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ('type', 'vigorous', 'start', 'duration')

    type = serializers.SlugRelatedField(
        slug_field='name',
        queryset = ActivityType.objects.filter(user=None).all()
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        if hasattr(instance, 'earned_minutes'):
            representation['earnedMinutes'] = instance.earned_minutes
        return representation

class FitbitDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = FitbitDay
        fields = ('date', 'moderate_minutes', 'vigorous_minutes', 'step_count')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_minutes'] = instance.moderate_minutes + instance.vigorous_minutes*2
        return representation

class FitbitActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FitbitActivity
        fields = ('type', 'start_time', 'end_time', 'vigorous_minutes', 'moderate_minutes')

    type = serializers.SlugRelatedField(
        slug_field='name',
        queryset = ActivityType.objects.filter(user=None).all()
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        
        representation['start'] = representation['start_time']
        del representation['start_time']
        representation['end'] = representation['end_time']
        del representation['end_time']

        representation['total_minutes'] = instance.moderate_minutes + instance.vigorous_minutes*2
        return representation
