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
    """Web API View for something related to Day-to-Day meanings. (TODO: should be described further)

    Extends:
        APIView
    """
    DATE_FORMAT = "%Y-%m-%d"

    permission_classes = [IsAuthenticated]

    def format_date(self, date):
        return date.strftime(self.DATE_FORMAT)

    def parse_date(self, day):
        """Convert standard datetime string to date object (delete hour/min/sec)"""
        try:
            dt = datetime.strptime(day, self.DATE_FORMAT).astimezone(pytz.UTC)
            return date(dt.year, dt.month, dt.day)
        except:
            raise ValueError("Invalid date format string: {}".format(day))

    def get_day_joined(self, user):
        """Returns the date when the user joined in user's local time"""
        service = DayService(user=user)
        return service.get_date_at(user.date_joined)

    def validate_date(self, user, day):
        """It raises 404 if the day is before the user's joining date
        TODO: change this into boolean"""
        day_joined = self.get_day_joined(user)
        if day < day_joined:
            raise Http404()
