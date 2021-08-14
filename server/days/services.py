import datetime
import pytz

from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from locations.services import LocationService

from .models import Day
from .models import User

class TimezoneService:

    def get_timezones(users, start, end):
        days = Day.objects.filter(
            user__in = users,
            date__gte = start,
            date__lte = end
        ).all()
        timezones = {}
        for day in days:
            if day.user.username not in timezones:
                timezones[day.user.username] = {}
            timezones[day.user.username][day.date] = day.get_timezone()
        return timezones


class DayService:

    class NoUser(ImproperlyConfigured):
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

    def get_day(self, dt):
        """Returns the first(?) Day object of a particular day.
        If there's none, create one.
        """
        if type(dt) is datetime.date:
            return self.get_day_for_date(dt)
        day = Day.objects.filter(
            user = self.__user,
            start__lte = dt,
            end__gt = dt
        ).first()
        if day:
            return day
        return self.create_day_for(dt)

    def get_day_for_date(self, date):
        try:
            return Day.objects.get(
                user = self.__user,
                date = date
            )
        except Day.DoesNotExist:
            return self.create_day_for(date)

    def create_day_for(self, dt):
        """create a Day object for a particular date object

        Args:
            dt (datetime)

        Returns:
            Day object
        """
        tz = self.get_best_timezone(dt)
        if type(dt) is datetime.datetime:
            dt = dt.astimezone(tz)
        day, _ = Day.objects.get_or_create(
            user = self.__user,
            date = datetime.date(dt.year, dt.month, dt.day),
            defaults = {
                'timezone': tz.zone
            }
        )
        return day

    def get_best_timezone(self, dt):
        if type(dt) is datetime.date:
            return self.get_best_timezone_for_date(dt)
        else:
            return self.get_best_timezone_for_datetime(dt)

    def get_best_timezone_for_date(self, dt):
        """returns the best guess for the timezone
            - if the last observed day exists, returns its timezone
            - if not, the first observed day from the date is returned
            - if not, return the default timezone
        """
        previous_day = Day.objects.filter(
            user = self.__user,
            date__lte = dt
        ).last()
        if previous_day:
            return previous_day.get_timezone()
        next_day = Day.objects.filter(
            user = self.__user,
            date__gte = dt
        ).first()
        if next_day:
            return next_day.get_timezone()
        return self.get_default_timezone()

    def get_best_timezone_for_datetime(self, dt):
        previous_day = Day.objects.filter(
            user = self.__user,
            end__lte = dt
        ).last()
        if previous_day:
            return previous_day.get_timezone()
        next_day = Day.objects.filter(
            user = self.__user,
            start__gte = dt
        ).first()
        if next_day:
            return next_day.get_timezone()
        return self.get_default_timezone()

    def update_current_day_timezone_to_default(self):
        """update Day object with default timezone

        Returns:
            updated timezone str
        """
        tz = self.get_default_timezone()
        day = self.get_day(timezone.now())
        day.timezone = tz
        day.save()
        
        return tz
        
    def get_default_timezone(self):
        service = LocationService(user = self.__user)
        return service.get_home_timezone()

    def get_timezone_at(self, dt):
        """Returns the time zone according to the location at a particular timepoint"""
        day = self.get_day(dt)
        return day.get_timezone()

    def get_current_timezone(self):
        """Returns the current time zone according to the latest location"""
        return self.get_timezone_at(timezone.now())

    def get_datetime_at(self, dt):
        tz = self.get_timezone_at(dt)
        if type(dt) is datetime.date:
            return tz.localize(datetime.datetime(
                dt.year,
                dt.month,
                dt.day
            ))
        return dt.astimezone(tz)

    def get_current_datetime(self):
        return self.get_datetime_at(timezone.now())

    def get_date_at(self, dt):
        dt = self.get_datetime_at(dt)
        return datetime.date(
            dt.year,
            dt.month,
            dt.day
        )

    def get_current_date(self):
        return self.get_date_at(timezone.now())
    
    def get_start_of_day(self, dt):
        local_datetime = self.get_datetime_at(dt)
        return local_datetime.replace(
            hour = 0,
            minute = 0,
            second = 0,
            microsecond = 0
        )

    def get_end_of_day(self, dt):
        return self.get_start_of_day(dt) + datetime.timedelta(days=1)
