from rest_framework import serializers
from datetime import datetime

from .models import SuggestionTime, TIMES

def parse_time(value):
    try:
        time = datetime.strptime(value, "%H:%M")
    except:
        return False
    return time

class TimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestionTime
        fields = ('type', 'hour', 'minute')

class SuggestionTimeSerializer(serializers.Serializer):
    times = TimeSerializer(many=True)

    def to_internal_value(self, data):
        times = []
        for key in data:
            if key not in TIMES:
                raise serializers.ValidationError({
                    key:"Incorrect key"
                    })
            time = parse_time(data[key])
            if not time:
                raise serializers.ValidationError({
                    key: "Invalid format"
                })
            times.append({
                'type': key,
                'hour': time.hour,
                'minute': time.minute
            })
        return {
            'times': times
        }

    def to_representation(self, obj):
        new_obj = {}
        for time in obj['times']:
            new_obj[time['type']] = "%s:%s" % (time['hour'], time['minute'])
        return new_obj