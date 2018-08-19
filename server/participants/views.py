from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

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
                participant = Participant.objects.get(enrollment_token__iexact=enrollment_token)
            except Participant.DoesNotExist:
                return Response({}, status.HTTP_400_BAD_REQUEST)
            if not participant.user:
                user, created = User.objects.get_or_create(
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
