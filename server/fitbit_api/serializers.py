from rest_framework import serializers

from fitbit_api.models import FitbitDay

class FitbitDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = FitbitDay
        fields = ('date', 'active_minutes', 'total_steps')
