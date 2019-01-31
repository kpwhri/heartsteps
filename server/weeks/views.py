from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Week
from .services import WeekService

class WeekView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_week(self, week_number, user):
        try:
            return Week.objects.get(
                number = week_number,
                user = user
            )
        except Week.DoesNotExist:
            raise Http404()

    def get_current_week(self, user):
        service = WeekService(user)
        try:
            return service.get_current_week()
        except WeekService.WeekDoesNotExist:
            last_week = Week.objects.last()
            return service.get_week_after(last_week)

    def get(self, request, week_number=None):
        if week_number is not None:
            week = self.get_week(week_number, request.user)
        else:
            week = self.get_current_week(request.user)
        return Response({
            'id': week.number,
            'start': week.start_date.strftime('%Y-%m-%d'),
            'end': week.end_date.strftime('%Y-%m-%d')
        }, status=status.HTTP_200_OK)

class NextWeekView(WeekView):

    def get(self, request, week_number):
        week = self.get_week(week_number, request.user)

        service = WeekService(request.user)
        next_week = service.get_week_after(week=week)
        return Response({
            'id': next_week.number,
            'start': next_week.start_date.strftime('%Y-%m-%d'),
            'end': next_week.end_date.strftime('%Y-%m-%d')
        }, status=status.HTTP_200_OK)
