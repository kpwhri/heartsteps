from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from .models import Device, Message, MessageReceipt

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('token', 'type')

class MessageReceiptSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super(MessageReceiptSerializer, self).__init__(*args, **kwargs)
        if 'context' in kwargs and 'user' in kwargs['context']:
            self.user = kwargs['context']['user']

    
    def to_internal_value(self, data):
        try:
            message = Message.objects.get(uuid=data['id'], recipient=self.user)
        except Message.DoesNotExist:
            raise serializers.ValidationError({
                'id': 'Message does not exist'
            })
        return_dict = {
            'message': message
        }
        for key in data:
            if key == 'id':
                continue
            if key not in MessageReceipt.MESSAGE_RECEIPT_TYPES:
                raise serializers.ValidationError({
                    key: 'Message receipt type does not exist'
                })
            try:
                time = datetime.strptime(data[key], '%Y-%m-%d %H:%M:%S')
                return_dict[key] = time.astimezone(timezone.get_current_timezone())
            except:
                raise serializers.ValidationError({
                    key: 'Invalid date time'
                })
        return return_dict

        

