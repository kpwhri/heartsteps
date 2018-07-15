from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from .models import Decision

class DecisionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        decision = Decision(
            user = request.user
        )
        decision.save()
        decision.get_context()
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
        
        # update context here
        decision.make_message()
        decision.send_message()

        return Response({}, status=status.HTTP_200_OK)


