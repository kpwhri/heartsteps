from datetime import datetime, date
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
    end_date = parse_date(end)

    results = Day.objects.filter(
        user = request.user,
        date__year__gte=start_date.year,
        date__month__gte=start_date.month,
        date__day__gte=start_date.day,
        date__year__lte=end_date.year,
        date__month__lte=end_date.month,
        date__day__lte=end_date.day
    ).order_by('date').all()
    serialized = DaySerializer(results, many=True)
    return Response(serialized.data, status=status.HTTP_200_OK)
