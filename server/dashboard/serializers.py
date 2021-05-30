from rest_framework import serializers, generics
from push_messages.models import Device, Message, MessageReceiptQuerySet

class PushMessageSerializer(serializers.ModelSerializer):
    # actual_objs = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['recipient', 'content', 'title', 'body']
        # testing new git login

    # type = serializers.SlugRelatedField(
    #     slug_field='recipient',
        # queryset = PushMessage.objects.filter(recipient=None).all()
    # )

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
        

    # def get_objs(actual_objs):
    #     return actual_objs.get_objs()
