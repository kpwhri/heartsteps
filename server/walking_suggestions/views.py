from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from locations.services import LocationService

from .models import WalkingSuggestionDecision, SuggestionTime
from .services import WalkingSuggestionDecisionService
from .tasks import make_decision

class WalkingSuggestionCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if 'category' in request.data and request.data['category'] in SuggestionTime.TIMES:
            service = WalkingSuggestionDecisionService.create_decision(
                user = request.user,
                category = request.data['category'],
                test = True
            )
            service.update_context()
            service.decide()
            service.send_message()
            return Response('', status = status.HTTP_201_CREATED)
        return Response('', status=status.HTTP_400_BAD_REQUEST)

class WalkingSuggestionContextView(APIView):
    """
    Updates a walking suggestion's context and starts make decision
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, decision_id):
        try:
            decision = WalkingSuggestionDecision.objects.get(id=decision_id)
        except WalkingSuggestionDecision.DoesNotExist:
            return Response('Not found', status=status.HTTP_404_NOT_FOUND)
        if decision.user != request.user:
            return Response('Wrong participant', status=status.HTTP_401_UNAUTHORIZED)
        
        if 'location' in request.data:
            location_service = LocationService(request.user)
            try:
                location = location_service.update_location(request.data['location'])
                decision.add_context_object(location)
            except LocationService.InvalidLocation:
                return Response('Invalid location', status=status.HTTP_400_BAD_REQUEST)
        make_decision.apply_async(kwargs={
            'decision_id': decision_id
        })
        return Response('', status=status.HTTP_200_OK)
