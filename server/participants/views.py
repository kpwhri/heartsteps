from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.contrib.auth.models import User

from .models import Participant
from .services import ParticipantService

class EnrollView(APIView):
    """
    Enrolls a participant and creates an enrollment token for their session if a matching token is found.

    Expects requests to send a "enrollmentToken" in post data.
    """
    def post(self, request, format=None):
        enrollment_token = request.data.get('enrollmentToken')
        birth_year = request.data.get('birthYear', None)
        if enrollment_token:
            try:
                service = ParticipantService.get_participant(
                    token = enrollment_token,
                    birth_year = birth_year
                )
            except ParticipantService.NoParticipant:
                return Response({}, status.HTTP_401_UNAUTHORIZED)

            service.initialize()
            auth_token = service.get_authorization_token()
            heartsteps_id = service.get_heartsteps_id()
            
            response_data = {
                'heartstepsId': heartsteps_id
            }
            response_headers = {
                'Authorization-Token': auth_token
            }

            return Response(response_data, headers=response_headers)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
