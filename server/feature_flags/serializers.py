from rest_framework import fields, serializers
from .models import FeatureFlags

class FeatureFlagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlags
        fields = [str('uuid'), 'notification_center_flag']
