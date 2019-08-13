from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import serializers
from twilio.twiml.messaging_response import Message, MessagingResponse

from .models import Message
from .services import SMSService

class TwilioMessageSerializer(serializers.Serializer):
    MessageSid = serializers.CharField()
    From = serializers.CharField()
    To = serializers.CharField()
    Body = serializers.CharField()


class TwilioReplyView(APIView):

    def template_response(self, template_name):
        if hasattr(settings, 'STUDY_PHONE_NUMBER'):
            contact_number = settings.STUDY_PHONE_NUMBER
        else:
            contact_number = '(555) 555-5555'
        
        response = MessagingResponse()
        message_text = render_to_string(
            template_name = template_name,
            context = {
                'contact_number': contact_number
            }
        )
        response.message(message_text)

        return HttpResponse(response)

    def default_response(self):
        return self.template_response('sms_messages/message_received.txt')

    def unknown_number_response(self):
        return self.template_response('sms_messages/unknown_contact.txt')

    def null_response(self):
        return HttpResponse(MessagingResponse())

    def post(self, request):
        serialized = TwilioMessageSerializer(data=request.data)
        if serialized.is_valid():
            received_message = Message.objects.create(
                external_id = serialized.validated_data['MessageSid'],
                recipient = serialized.validated_data['To'],
                sender = serialized.validated_data['From'],
                body = serialized.validated_data['Body']
            )
            try:
                service = SMSService(phone_number = received_message.sender)
                return self.default_response()
            except SMSService.UnknownContact:
                return self.unknown_number_response()
        else:
            return self.default_response()



