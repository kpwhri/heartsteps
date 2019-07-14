from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from locations.services import LocationService

from .models import WalkingSuggestionDecision, SuggestionTime
from .services import WalkingSuggestionDecisionService

class WalkingSuggestionCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if 'category' in request.data and request.data['category'] in SuggestionTime.TIMES:
            service = WalkingSuggestionDecisionService.create_decision(
                user = request.user,
                category = request.data['category'],
                test = True
            )
            WalkingSuggestionDecisionService.process_decision(
                decision = service.decision
            )
            return Response('', status = status.HTTP_201_CREATED)
        return Response('', status=status.HTTP_400_BAD_REQUEST)
