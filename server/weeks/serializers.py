from datetime import datetime

from rest_framework import serializers

from surveys.serializers import SurveySerializer

from .models import Week

class WeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Week
        fields = ('number', 'start_date', 'end_date', 'goal', 'confidence')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = representation['number']
        representation['start'] = representation['start_date']
        representation['end'] = representation['end_date']
        del representation['number']
        del representation['start_date']
        del representation['end_date']

        return representation

class GoalSerializer(serializers.Serializer):
    goal = serializers.IntegerField()
    confidence = serializers.FloatField()
