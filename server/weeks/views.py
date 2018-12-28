from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Week
from .services import WeekService

class WeekView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        service = WeekService(request.user)
        week = service.get_current_week()
        return Response({
            'id': week.id,
            'start': week.start_date.strftime('%Y-%m-%d'),
            'end': week.end_date.strftime('%Y-%m-%d')
        }, status=status.HTTP_200_OK)