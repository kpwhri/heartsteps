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
            EventLog.debug(None, "token: {}, birth_year: {} 79a459ba-e4c8-4391-9bc4-f2ae1c58d187".format(enrollment_token, birth_year))
        except ParticipantService.NoParticipant:
            EventLog.debug(None, "05c28a14-b582-4299-a1f5-a2e47d5b3133")
            return Response({}, status.HTTP_401_UNAUTHORIZED)
        EventLog.debug(None, "acfe92ad-1a34-4d9d-8b4d-b2c836bc323e")
        try:
            service.initialize()
        except Exception as e:
            EventLog.debug(None, e)
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
        EventLog.debug(request.user, "4dfb1f9f-2970-4db5-8185-6d9ea4f17fdf")
        try:
            EventLog.debug(request.user, "77ee7a7c-0c66-4e32-b7ba-5a69e053a56a")
            service = ParticipantService(user = request.user)
            EventLog.debug(request.user, "ee51e8ef-36f8-44ff-ba26-2008c6954893")
        except ParticipantService.NoParticipant:
            EventLog.debug(request.user, "d3f281fd-bd95-469a-89fa-8519756e3397")
            return Response('No participant for user', status=status.HTTP_404_NOT_FOUND)
        EventLog.debug(request.user, "ede2faac-2687-407e-8777-050f5a3d3d10")
        
        return_dict = {}
        
        EventLog.debug(request.user, "constructing return_dict")
        return_dict['heartstepsId'] = service.get_heartsteps_id()
        EventLog.debug(request.user)
        return_dict['staff'] = request.user.is_staff
        EventLog.debug(request.user)
        return_dict['date_enrolled'] = service.participant.date_joined.strftime('%Y-%m-%d')
        EventLog.debug(request.user)
        return_dict['studyContactName'] = service.get_study_contact_name()
        EventLog.debug(request.user)
        return_dict['studyContactNumber'] = service.get_study_contact_number()
        EventLog.debug(request.user)
        return_dict['baselinePeriod'] = service.get_baseline_period()
        EventLog.debug(request.user)
        return_dict['baselineComplete'] = service.is_baseline_complete()
        EventLog.debug(request.user)
        return_dict['participantTags'] = []
        EventLog.debug(request.user)
        return Response(return_dict)


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
