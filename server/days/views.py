from datetime import datetime
from datetime import date
import pytz

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.http import Http404

from .services import DayService

class DayView(APIView):

    DATE_FORMAT = "%Y-%m-%d"

    permission_classes = [IsAuthenticated]

    def format_date(self, date):
        return date.strftime(self.DATE_FORMAT)

    def parse_date(self, day):
        try:
            dt = datetime.strptime(day, self.DATE_FORMAT).astimezone(pytz.UTC)
            return date(dt.year, dt.month, dt.day)
        except:
            raise Http404()

    def get_day_joined(self, user):
        service = DayService(user=user)
        return service.get_date_at(user.date_joined)

    def validate_date(self, user, day):
        day_joined = self.get_day_joined(user)
        if day < day_joined:
            raise Http404()
