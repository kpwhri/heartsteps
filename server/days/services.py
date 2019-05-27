from datetime import date
import pytz

from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from .models import Day
from .models import User

class DayService:

    class NoUser(ImproperlyConfigured):
        pass

    class InvalidDateTime(RuntimeError):
        pass

    def __init__(self, user=None, username=None):
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise self.NoUser("Username does not exist")
        if not user:
            raise self.NoUser("No user")
        self.__user = user

    def check_valid_datetime(self, datetime):
        if datetime < self.__user.date_joined:
            raise self.InvalidDateTime('Before user joined')

    def get_day(self, datetime):
        self.check_valid_datetime(datetime)
        day = Day.objects.filter(
            user = self.__user,
            start__lte = datetime,
            end__gt = datetime
        ).first()
        if day:
            return day
        return self.create_day_for(datetime)

    def create_day_for(self, datetime):
        self.check_valid_datetime(datetime)
        previous_day = Day.objects.filter(
            user = self.__user,
            end__lte = datetime
        ).last()
        if previous_day:
            tz = previous_day.get_timezone()
            dt = datetime.astimezone(tz)
            day = Day.objects.create(
                user = self.__user,
                date = date(dt.year, dt.month, dt.day),
                timezone = previous_day.timezone
            )
            return day
        else:
            raise InvalidDateTime('Unknown datetime')

    def create_default_day_for(self, datetime):
        self.check_valid_datetime(datetime)
        return Day.objects.create(
            user = self.__user,
            date = date(datetime.year, datetime.month, datetime.day),
            timezone = "UTC"
        )

    def get_timezone_at(self, datetime):
        day = self.get_day(datetime)
        return day.get_timezone()

    def get_current_timezone(self):
        return self.get_timezone_at(timezone.now())

    def get_datetime_at(self, datetime):
        tz = self.get_timezone_at(datetime)
        return datetime.astimezone(tz)

    def get_current_datetime(self):
        return self.get_datetime_at(timezone.now())

    def get_date_at(self, datetime):
        dt = self.get_datetime_at(datetime)
        return date(
            dt.year,
            dt.month,
            dt.day
        )

    def get_current_date(self):
        return self.get_date_at(timezone.now())
