from rest_framework import serializers

from surveys.serializers import SurveySerializer
from morning_messages.models import MorningMessage

class MorningMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MorningMessage
        fields = ('date', 'notification', 'text', 'anchor')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.survey:
            serializedSurvey = SurveySerializer(instance.survey)
            representation['survey'] = serializedSurvey.data
        return representation