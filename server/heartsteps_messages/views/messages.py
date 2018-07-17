from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from heartsteps_messages.models import Message

class RecievedMessageView(APIView):
    """
    Checks if the message_id that was sent matches the current user, and of so
    marks the message as recieved with the current datetime.

    If the message has already been recieved, the recieved datetime is not
    udpated.
    """
    def post(self, request):
        message_id = request.data.get('messageId')
        if message_id:
            try:
                message = Message.objects.get(id=message_id)
            except Message.DoesNotExist:
                return Response({}, status.HTTP_404_NOT_FOUND)
            
            if request.user != message.reciepent:
                return Response({}, status.HTTP_401_UNAUTHORIZED)

            if not message.recieved:
                message.markRecieved()
                message.save()
                return Response({}, status.HTTP_201_CREATED)
            return Response({}, status.HTTP_200_OK)
        return Response({}, status.HTTP_400_BAD_REQUEST)
