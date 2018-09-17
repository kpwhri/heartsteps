from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import Message, Device, MessageReciept
from .serializers import DeviceSerializer, MessageRecieptSerializer

from django.utils import timezone

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
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = MessageRecieptSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data['message']
            
            if request.user != message.recipient:
                return Response({}, status.HTTP_401_UNAUTHORIZED)

            try:
                message_reciept = MessageReciept.objects.get(
                    message = message,
                    type = serializer.validated_data['type']
                    )
            except MessageReciept.DoesNotExist:
                message_reciept = MessageReciept.objects.create(
                    message = message,
                    type = serializer.validated_data['type'],
                    time = serializer.validated_data['time']
                )
                return Response({}, status.HTTP_201_CREATED)
            return Response({}, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
