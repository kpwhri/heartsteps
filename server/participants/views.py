from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.contrib.auth.models import User

from .models import Participant
from .services import ParticipantService

class LoginView(APIView):

    def post(self, request):
        enrollment_token = request.data.get('enrollmentToken')
        birth_year = request.data.get('birthYear', None)
        if enrollment_token:
            try:
                service = ParticipantService.get_participant(
                    token = enrollment_token,
                    birth_year = birth_year
                )
                self.service = service
                self.participant = service.participant
            except ParticipantService.NoParticipant:
                return Response({}, status.HTTP_401_UNAUTHORIZED)
            self.authentication_successful()
            return Response(
                self.get_response(),
                headers=self.get_headers()
            )
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def get_response(self):
        return {
            'heartstepsId': self.service.get_heartsteps_id()
        }

    def get_headers(self):
        return {
            'Authorization-Token': self.service.get_authorization_token()
        }

    def authentication_successful(self):
        pass

class EnrollView(LoginView):

    def authentication_successful(self):
        self.service.initialize()
