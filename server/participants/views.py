from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.authtoken.models import Token

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

class FirebaseTokenView(APIView):
    """
    Manages the enrollment token for the current participant

    token should only be passed with the key "token"
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.data.get('token'):
            try:
                participant = Participant.objects.get(user=request.user)
                participant.firebase_token = request.data.get('token')
                participant.save()
                return Response({})
            except:
                pass
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

