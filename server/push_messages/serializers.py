from rest_framework import serializers
from .models import Device, MessageReceipt

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('token', 'type')

class MessageReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReceipt
        fields = ('message', 'time', 'type')