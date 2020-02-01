from rest_framework import serializers

from .models import FitbitAccount

class FitbitAccountSerializer(serializers.Serializer):
    id = serializers.CharField(source='fitbit_user')
    isAuthorized = serializers.BooleanField(source='authorized')
    firstUpdated = serializers.DateTimeField(source='first_updated')
    lastUpdated = serializers.DateTimeField(source='last_updated')
    lastDeviceUpdate = serializers.DateTimeField(source='last_device_update')

    class Meta:
        model = FitbitAccount
        fields = []
