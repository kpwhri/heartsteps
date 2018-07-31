from rest_framework import serializers
from datetime import datetime

from .models import SuggestionTime, TIMES

def parse_time(value):
    try:
        time = datetime.strptime(value, "%H:%M")
    except:
        return False
    return time

class SuggestionTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestionTime
        fields = ('id', 'type', 'hour', 'minute', 'timezone')