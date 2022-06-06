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
from push_messages.models import Device

from user_event_logs.models import EventLog

class LogoutView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            service = ParticipantService(user = request.user)
        except ParticipantService.NoParticipant:
            return Response({}, status.HTTP_400_BAD_REQUEST)
        try:
            my_devices = Device.objects.filter(user=request.user, active=True)
        except:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        # TODO: should only be one device but redunancy for safety here
        for device in my_devices:
            device.active = False
            device.save()

        service.destroy_authorization_token()
        service.disable()

        return Response({}, status.HTTP_200_OK)


class LoginView(APIView):

    def post(self, request):
        # print("LoginView.post()")
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
        
        try:
            service.initialize()
        except Exception as e:
            EventLog.error(None, e)
        
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
        
        return_dict = {}
        
        return_dict['heartstepsId'] = service.get_heartsteps_id()
        return_dict['staff'] = request.user.is_staff
        return_dict['date_enrolled'] = service.participant.date_joined.strftime('%Y-%m-%d')
        return_dict['studyContactName'] = service.get_study_contact_name()
        return_dict['studyContactNumber'] = service.get_study_contact_number()
        return_dict['baselinePeriod'] = service.get_baseline_period()
        return_dict['baselineComplete'] = service.is_baseline_complete()
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
