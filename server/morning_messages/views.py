import pytz
from datetime import datetime, date

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from locations.services import LocationService

from .services import MorningMessageService
from .serializers import MorningMessageSerializer

def format_date(date):
    return datetime.strftime(date, '%Y-%m-%d')

def parse_date(day):
    try:
        dt = datetime.strptime(day, '%Y-%m-%d').astimezone(pytz.UTC)
        return date(dt.year, dt.month, dt.day)
    except:
        raise Http404()

def get_day_joined(user):
    location_service = LocationService(user)
    tz = location_service.get_current_timezone()
    date_joined = user.date_joined.astimezone(tz)
    return date(
        date_joined.year,
        date_joined.month,
        date_joined.day
    )

def check_valid_date(user, day):
    day_joined = get_day_joined(user)
    if day < day_joined:
        raise Http404()

class MorningMessageView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, day):
        request_date = parse_date(day)
        check_valid_date(request.user, request_date)
        morning_message_service = MorningMessageService(
            user = request.user
        )
        morning_message, _ = morning_message_service.get_or_create(request_date)
        serialized = MorningMessageSerializer(morning_message)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, day):
        request_date = parse_date(day)
        check_valid_date(request.user, request_date)
        morning_message_service = MorningMessageService(user = request.user)
        morning_message_service.send_notification(request_date)
        return Response({}, status=status.HTTP_201_CREATED)