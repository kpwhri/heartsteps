from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.authtoken.models import Token
from fcm_django.models import FCMDevice

from .models import Participant


class EnrollView(APIView):
    """
    Enrolls a participant and creates an enrollment token for their session if a matching token is found.

    Expects requests to send a "enrollment_token" in post data.
    """
    def post(self, request, format=None):
        if request.data.get('enrollment_token'):
            try:
                participant = Participant.objects.get(enrollment_token=request.data.get('enrollment_token'))
                token, created = Token.objects.get_or_create(user=participant.user)
                return Response({
                    'token': token.key,
                    'participant_id': participant.id
                })
            except Participant.DoesNotExist:
                pass
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

class Device(APIView):
    """
    Updates the device that is used for Firebase Cloud Messages

    Expects two arguments, registration and type, which are the FCM token
    and device that the token was made on.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.data.get('registration') and request.data.get('device_type'):
            try:
                participant = Participant.objects.get(user=request.user)
            except:
                return Response({}, status=status.HTTP_401_UNAUTHORIZED)

            device = FCMDevice.objects.create(
                registration_id = request.data.get('registration'),
                type = request.data.get('device_type'),
                user = request.user
            )
            return Response({})
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

