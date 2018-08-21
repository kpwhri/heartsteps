from rest_framework import serializers
from .models import Device, MessageReciept

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('token', 'type')

class MessageRecieptSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReciept
        fields = ('message', 'time', 'type')