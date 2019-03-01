from django.utils import timezone


from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from locations.services import LocationService

from .models import WalkingSuggestionDecision, SuggestionTime
from .services import AntiSedentaryDecisionService
from .tasks import make_decision

class AntiSedentaryMessageCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        decision_service = AntiSedentaryDecisionService.create_decision(
            user = request.user,
            test = True
        )
        decision_service.decide()
        decision_service.update_context()
        decision_service.send_message()
        return Response('', status = status.HTTP_201_CREATED)

