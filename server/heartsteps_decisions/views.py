from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import uuid

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
