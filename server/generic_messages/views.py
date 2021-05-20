from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .services import GenericMessagesService

class GenericMessagesMessageCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        generic_messages_service = GenericMessagesService.create_service(
            username = request.user.username
        )
        message = generic_messages_service.send_message("test intervention", "Notification.GenericMessagesTest", "Sample Title", "Sample Body", False)
        return Response(
            {
                'messageId': str(message.data["messageId"])
            },
            status = status.HTTP_201_CREATED
        )

