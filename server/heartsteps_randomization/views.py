from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from .models import Decision, Location

from .tasks import create_decision, make_decision

class DecisionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        create_decision.delay(request.user.username)
        return Response({}, status=status.HTTP_201_CREATED)

class DecisionUpdateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, decision_id):
        try:
            decision = Decision.objects.get(id=decision_id)
        except Decision.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        if decision.user.id is not request.user.id:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        
        if 'location' in request.data and not hasattr(decision, 'location'):
            location = request.data['location']
            Location.objects.create(
                decision = decision,
                lat = float(location['lat']),
                long = float(location['lng'])
            )
            return Response({}, status=status.HTTP_201_CREATED)

        result = make_decision.delay(str(decision.id))
        return Response({}, status=status.HTTP_200_OK)


