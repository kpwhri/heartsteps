from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import Message, Device
from .serializers import DeviceSerializer

class DeviceView(APIView):
    """
    Manage a user's Firebase Cloud Messaging Device
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            device = Device.objects.get(user=request.user, active=True)
        except Device.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        serialized_device = DeviceSerializer(device)
        return Response(serialized_device.data, status=status.HTTP_200_OK)


    def post(self, request):
        serialized_device = DeviceSerializer(data=request.data, context={
            'user': request.user
        })
        if serialized_device.is_valid():
            Device.objects.filter(user=request.user, active=True).update(active=False)

            Device.objects.create(
                user = request.user,
                token = serialized_device.validated_data['token'],
                type = serialized_device.validated_data['type'],
                active = True
            )
            return Response(serialized_device.data, status=status.HTTP_201_CREATED)

        return Response({}, status=status.HTTP_400_BAD_REQUEST)


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
