from rest_framework import serializers

from morning_messages.models import MorningMessage

class MorningMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MorningMessage
        fields = ('date', 'notification', 'text', 'anchor')
