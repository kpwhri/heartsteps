from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from locations.services import LocationService

from .models import WalkingSuggestionDecision
from .tasks import make_decision

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
