from django.shortcuts import render
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from .models import Decision

from .tasks import make_decision

class DecisionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        decision = Decision.objects.create(
            user = request.user,
            time = timezone.now()
        )

        make_decision.delay(str(decision.id))
        return Response({}, status=status.HTTP_201_CREATED)
