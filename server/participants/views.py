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

from user_event_logs.models import EventLog

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
        EventLog.debug(None, "LoginView Post 6c0337d6-5aac-4d76-a255-12136b1b26f4")
        enrollment_token = request.data.get('enrollmentToken')
        EventLog.debug(None, "enrollmentToken b775323c-eb39-4d13-8d7e-c570107aac14")
        birth_year = request.data.get('birthYear', None)
        EventLog.debug(None, "birth_year 254ae59d-b788-4b7f-8ce4-cca622b175a3")
        if not enrollment_token:
            EventLog.debug(None, "no enrollment_token cdab1516-53c4-4401-a1ca-3310ec05a4ea")
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        try:
            EventLog.debug(None, "1b89c75f-d4a8-41f3-bb6b-dd7ee89add62")
            service = ParticipantService.get_participant(
                token = enrollment_token,
                birth_year = birth_year
            )
            EventLog.debug(None, "79a459ba-e4c8-4391-9bc4-f2ae1c58d187")
        except ParticipantService.NoParticipant:
            EventLog.debug(None, "05c28a14-b582-4299-a1f5-a2e47d5b3133")
            return Response({}, status.HTTP_401_UNAUTHORIZED)
        EventLog.debug(None, "acfe92ad-1a34-4d9d-8b4d-b2c836bc323e")
        service.initialize()
        EventLog.debug(None, "e34818d7-8f67-4319-ba62-a2291b580863")

        return Response(
            {
                'heartstepsId': service.get_heartsteps_id()
            },
            headers = {
                'Authorization-Token': service.get_authorization_token()
            }
        )

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
            'date_enrolled': service.participant.date_joined.strftime('%Y-%m-%d'),
            'studyContactName': service.get_study_contact_name(),
            'studyContactNumber': service.get_study_contact_number(),
            'baselinePeriod': service.get_baseline_period(),
            'baselineComplete': service.is_baseline_complete(),
            'participantTags': []
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
