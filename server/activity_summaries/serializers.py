from rest_framework import serializers

from fitbit_activities.models import FitbitDay, FitbitActivity

from activity_logs.models import ActivityLog, ActivityType

from .models import ActivitySummary
from .models import Day

class ActivitySummarySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ActivitySummary
        fields = (
            'activities_completed',
            'miles',
            'minutes',
            'steps',
            'updated'
        )

class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = (
            'date',
            'moderate_minutes',
            'vigorous_minutes',
            'steps',
            'miles',
            'updated',
            'activities_completed'
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['wore_fitbit'] = instance.wore_fitbit

        representation['minutes'] = instance.total_minutes
        representation['moderateMinutes'] = representation['moderate_minutes']
        del representation['moderate_minutes']
        representation['vigorousMinutes'] = representation['vigorous_minutes']
        del representation['vigorous_minutes']
        representation['activitiesCompleted'] = representation['activities_completed']
        del representation['activities_completed']
        return representation
