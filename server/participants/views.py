from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from fcm_django.models import FCMDevice

from .models import Participant


class EnrollView(APIView):
    """
    Enrolls a participant and creates an enrollment token for their session if a matching token is found.

    Expects requests to send a "enrollmentToken" in post data.
    """
    def post(self, request, format=None):
        enrollment_token = request.data.get('enrollmentToken')
        if enrollment_token:
            try:
                participant = Participant.objects.get(enrollment_token=enrollment_token)
            except Participant.DoesNotExist:
                return Response({}, status.HTTP_400_BAD_REQUEST)
            if not participant.user:
                user = User.objects.create(
                    username= participant.heartsteps_id
                )
                participant.user = user
                participant.save()
            token, created = Token.objects.get_or_create(user=participant.user)

            response_data = {
                'heartstepsId': participant.heartsteps_id
            }
            response_headers = {
                'Authorization-Token': token
            }

            return Response(response_data, headers=response_headers)
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

