import pytz
from datetime import datetime

from rest_framework import serializers

from .models import SuggestionTime

class SuggestionTimeSerializer(serializers.Serializer):

    def to_internal_value(self, data):
        ret = {}
        for time_category in SuggestionTime.TIMES:
            if time_category not in data:
                raise serializers.ValidationError({
                    time_category: 'Required'
                })
            value = data[time_category]
            try:
                time = datetime.strptime(value, "%H:%M")
            except:
                raise serializers.ValidationError({
                    time_category: 'Not valid time'
                })
            ret[time_category] = {
                'hour': time.hour,
                'minute': time.minute
            }
        return ret
        