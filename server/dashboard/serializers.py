from rest_framework import serializers
from push_messages.models import Device, Message as PushMessage

class PushMessageSerializer(serializers.ModelSerializer):
    # actual_objs = serializers.SerializerMethodField()

    class Meta:
        model = PushMessage
        fields = ('__all__')

    # type = serializers.SlugRelatedField(
    #     slug_field='recipient',
        # queryset = PushMessage.objects.filter(recipient=None).all()
    # )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        

    # def get_objs(actual_objs):
    #     return actual_objs.get_objs()
