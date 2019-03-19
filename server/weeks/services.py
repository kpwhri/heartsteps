from datetime import timedelta, datetime, date

from django.utils import timezone

from locations.services import LocationService
from push_messages.services import PushMessageService

from .models import Week, User
from .serializers import WeekSerializer

class WeekService:

    class WeekDoesNotExist(Week.DoesNotExist):
        pass

    def __init__(self, user=None, username=None):
        if username:
            user = User.objects.get(username=username)
        self.__user = user

    def update_weeks(self):
        location_service = LocationService(self.__user)
        tz = location_service.get_current_timezone()
        now = timezone.now().astimezone(tz)
        start_date = self.__user.date_joined.astimezone(tz)

        week = self.get_or_create_week(start_date)
        while week.end < now:
            next_day = week.end + timedelta(days=1)
            week = self.get_or_create_week(next_day)
    
    def get_or_create_week(self, day):
        try:
            return self.get_week(day)
        except WeekService.WeekDoesNotExist:
            return self.create_week(day)

    def create_week(self, day):
        if type(day) is datetime:
            day = date(day.year, day.month, day.day)
        weekday = day.weekday()
        start_date = day - timedelta(days=weekday)
        end_date = start_date + timedelta(days=6)
        return Week.objects.create(
            user=self.__user,
            start_date = start_date,
            end_date = end_date
        )
    
    def get_week_after(self, week):
        next_week_start_day = week.end_date + timedelta(days=1)
        return self.get_or_create_week(next_week_start_day)

    def get_week(self, day):
        try:
            return Week.objects.get(
                user = self.__user,
                start_date__lte = day,
                end_date__gte = day
            )
        except Week.DoesNotExist:
            raise WeekService.WeekDoesNotExist()

    def get_current_week(self):
        location_service = LocationService(self.__user)
        now = location_service.get_current_datetime()
        return self.get_week(date(now.year, now.month, now.day))
    
    def get_next_week(self):
        location_service = LocationService(self.__user)
        now = location_service.get_current_datetime()
        next_week = now + timedelta(days=7)
        return self.get_or_create_week(date(next_week.year, next_week.month, next_week.day))

    def send_reflection(self, week):
        next_week = self.get_week_after(week)
        # Reset week goal, incase it was maniputlated
        # (which probably happened in testing)
        next_week.goal = next_week.get_default_goal()
        next_week.save()

        week_serialized = WeekSerializer(week)
        next_week_serialized = WeekSerializer(next_week)

        push_message_service = PushMessageService(user=self.__user)
        message = push_message_service.send_data({
            'type': 'weekly-reflection',
            'currentWeek': week_serialized.data,
            'nextWeek': next_week_serialized.data
        })        
