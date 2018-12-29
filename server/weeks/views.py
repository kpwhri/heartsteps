from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Week
from .services import WeekService

class WeekView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_week(self, week_id, user):
        try:
            return Week.objects.get(
                uuid = week_id,
                user = user
            )
        except Week.DoesNotExist:
            raise Http404()

    def get(self, request, week_id=None):
        if week_id is not None:
            week = self.get_week(week_id, request.user)
        else:
            service = WeekService(request.user)
            week = service.get_current_week()
        return Response({
            'id': week.id,
            'start': week.start_date.strftime('%Y-%m-%d'),
            'end': week.end_date.strftime('%Y-%m-%d')
        }, status=status.HTTP_200_OK)

class NextWeekView(WeekView):

    def get(self, request, week_id):
        week = self.get_week(week_id, request.user)

        service = WeekService(request.user)
        next_week = service.get_week_after(week=week)

        return Response({
            'id': next_week.id,
            'start': next_week.start_date.strftime('%Y-%m-%d'),
            'end': next_week.end_date.strftime('%Y-%m-%d')
        }, status=status.HTTP_200_OK)
