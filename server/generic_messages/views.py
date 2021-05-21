from django.http import HttpRequest

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from .services import GenericMessagesService

class GenericMessagesMessageCreateView(APIView):

    class BadRequestError(RuntimeError):
        pass
    
    class NoUserError(RuntimeError):
        pass
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        assert isinstance(request, Request), (
            'The `request` argument must be an instance of '
            '`django.http.HttpRequest`, not `{}.{}`.'
            .format(request.__class__.__module__, request.__class__.__name__)
        )
        assert hasattr(request, "user"), (
            "request does not have 'user' attribute."
        )
        
        generic_messages_service = GenericMessagesService.create_service(
            username = request.user.username
        )
        message = generic_messages_service.send_message("test intervention", "Notification.GenericMessagesTest", "Sample Title", "Sample Body", True)
        return Response(
            {
                'messageId': str(message.data["messageId"])
            },
            status = status.HTTP_201_CREATED
        )

