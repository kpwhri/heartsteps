from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Participant
from .serializers import ParticipantAddSerializer
from .services import ParticipantService


class LogoutView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            service = ParticipantService(user = request.user)
        except ParticipantService.NoParticipant:
            return Response({}, status.HTTP_400_BAD_REQUEST)
        service.destroy_authorization_token()
        service.disable()
        return Response({}, status.HTTP_200_OK)


class LoginView(APIView):

    def post(self, request):
        enrollment_token = request.data.get('enrollmentToken')
        birth_year = request.data.get('birthYear', None)
        if not enrollment_token:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = ParticipantService.get_participant(
                token = enrollment_token,
                birth_year = birth_year
            )
        except ParticipantService.NoParticipant:
            return Response({}, status.HTTP_401_UNAUTHORIZED)

        self.service = service
        self.participant = service.participant
        self.authentication_successful()

        return Response(
            self.get_response(),
            headers=self.get_headers()
        )

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


class ParticipantInformationView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            service = ParticipantService(user = request.user)
        except ParticipantService.NoParticipant:
            return Response('No participant for user', status=status.HTTP_404_NOT_FOUND)
        return Response({
            'heartstepsId': service.get_heartsteps_id(),
            'staff': request.user.is_staff,
            'date_enrolled': service.participant.date_enrolled.strftime('%Y-%m-%d')
        })


class ParticipantAddView(APIView):
    """
    Add base data for a new participant to enroll.
    """
    def post(self, request):
        # if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ParticipantAddSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
