from rest_framework import serializers

from surveys.serializers import SurveySerializer
from morning_messages.models import MorningMessage, MorningMessageSurvey

class MorningMessageSurveySerializer(SurveySerializer):
    class Meta:
        model = MorningMessageSurvey
        fields = []

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.word_set:
            representation['wordSet'] = instance.word_set

        return representation

class MorningMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MorningMessage
        fields = ('date', 'notification', 'text', 'anchor')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.survey:
            serializedSurvey = MorningMessageSurveySerializer(instance.survey)
            representation['survey'] = serializedSurvey.data
        return representation