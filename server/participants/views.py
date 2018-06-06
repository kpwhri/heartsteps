from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from rest_framework.authtoken.models import Token

from .models import Participant

@api_view(['POST'])
def enroll(request):
    if request.method == 'POST' and request.data.get('enrollment_token'):
        try:
            participant = Participant.objects.get()
            token, created = Token.objects.get_or_create(user=participant.user)
            return Response({
                'token': token.key,
                'participant_id': participant.id
            })
        except Participant.DoesNotExist:
            pass
    return Response({}, status=status.HTTP_400_BAD_REQUEST)
