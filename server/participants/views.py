from rest_framework.views import APIView
from rest_framework import status
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
