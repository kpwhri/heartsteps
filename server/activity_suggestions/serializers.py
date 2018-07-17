from rest_framework import serializers
from .models import SuggestionTime

class SuggestionTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestionTime
        fields = ('type', 'time_of_day')