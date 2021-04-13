from datetime import datetime, date, timedelta
import pytz

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from days.views import DayView
from fitbit_activities.services import FitbitDayService

from .models import ActivitySummary
from .models import Day

from .serializers import ActivitySummarySerializer
from .serializers import DaySerializer

def get_summary(user, date):
    day_query = Day.objects.filter(
        user = user,
        date = date
    ).order_by('updated')
    if day_query.count() > 0:
        return day_query.last()
    else:
        day = Day.objects.create(
            user = user,
            date = date
        )
        day.update_from_activities()
        day.update_from_fitbit()
        return day


class DaySummaryView(DayView):

    def get(self, request, day):
        day = self.parse_date(day)
        self.validate_date(request.user, day)
        summary = get_summary(request.user, day)
        serialized = DaySerializer(summary)
        return Response(serialized.data, status=status.HTTP_200_OK)

class DateRangeSummaryView(DayView):

    def get(self, request, start, end):
        start_date = self.parse_date(start)
        end_date = self.parse_date(end)
        day_joined = self.get_day_joined(request.user)

        if start_date < day_joined:
            start_date = day_joined
        if end_date < day_joined:
            raise Http404()

        if start_date > end_date:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        results = Day.objects.filter(
            user = request.user,
            date__range=[start_date, end_date]
        ).order_by('date').all()
        results = list(results)

        summaries = []
        index_date = start_date
        while index_date <= end_date:
            if results and results[0].date == index_date:
                summaries.append(results.pop(0))
            else:
                day = Day.objects.create(
                    user = request.user,
                    date = index_date
                )
                day.update_from_fitbit()
                day.update_from_activities()
                summaries.append(day)
            index_date = index_date + timedelta(days=1)
        serialized = DaySerializer(summaries, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

class DaySummaryUpdateView(DayView):

    def get(self, request, day):
        date = self.parse_date(day)
        self.validate_date(request.user, date)
        try:
            service = FitbitDayService(
                date = date,
                user = request.user
                )
            service.update()
        except:
            return Response('Fitbit update failed', status=status.HTTP_400_BAD_REQUEST)
        summary = get_summary(request.user, date)
        serialized = DaySerializer(summary)
        return Response(serialized.data, status=status.HTTP_200_OK)

class ActivitySummaryView(APIView):

    def get(self, request):
        summary = ActivitySummary.objects.filter(
            user = request.user
        ).last()
        if not summary:
            summary = ActivitySummary.objects.create(
                user = request.user
            )
            summary.update()
        serialized = ActivitySummarySerializer(summary)
        return Response(serialized.data, status.HTTP_200_OK)

