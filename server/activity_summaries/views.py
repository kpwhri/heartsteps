from datetime import datetime, date, timedelta
import pytz

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import Day
from .serializers import DaySerializer

def format_date(date):
    return datetime.strftime(date, '%Y-%m-%d')

def parse_date(day):
    try:
        dt = datetime.strptime(day, '%Y-%m-%d').astimezone(pytz.UTC)
        return date(dt.year, dt.month, dt.day)
    except:
        raise Http404()

def check_valid_date(user, date):
    dt = datetime(date.year, date.month, date.day).astimezone(pytz.UTC)
    if dt < user.date_joined:
        raise Http404()

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def day_summary(request, day):
    date = parse_date(day)
    check_valid_date(request.user, date)
    try:
        day = Day.objects.get(
            user = request.user,
            date__year = date.year,
            date__month = date.month,
            date__day = date.day
        )
    except Day.DoesNotExist:
        day = Day.objects.create(
            user = request.user,
            date = date
        )
        day.update_from_fitbit()
        day.update_from_activities()
    
    serialized = DaySerializer(day)
    return Response(serialized.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def date_range_summary(request, start, end):
    start_date = parse_date(start)
    check_valid_date(request.user, start_date)
    end_date = parse_date(end)
    check_valid_date(request.user, end_date)

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
