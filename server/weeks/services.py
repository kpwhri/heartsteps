from datetime import timedelta, date

from locations.services import LocationService

from .models import Week, User

class WeekService:

    class WeekDoesNotExist(Week.DoesNotExist):
        pass

    def __init__(self, user=None, username=None):
        if username:
            user = User.objects.get(username=username)
        self.__user = user

    def create_week(self, start_date=None, end_date=None):
        if start_date and end_date:
            pass
        elif start_date:
            end_date = start_date + timedelta(days=6)
        elif end_date:
            start_date = end_date - timedelta(days=6)
        else:
            start_date = date.today()
            end_date = start_date + timedelta(days=6)
        
        return Week.objects.create(
            user=self.__user,
            start_date = start_date,
            end_date = end_date
        )
    
    def get_week_after(self, week):
        next_week_start_day = week.end_date + timedelta(days=1)
        try:
            return self.get_week_for_date(next_week_start_day)
        except WeekService.WeekDoesNotExist:
            return self.create_week(start_date=next_week_start_day)

    def get_week_for_date(self, date):
        try:
            return Week.objects.get(
                user = self.__user,
                start_date__lte = date,
                end_date__gte = date
            )
        except Week.DoesNotExist:
            raise WeekService.WeekDoesNotExist()

    def get_current_week(self):
        location_service = LocationService(self.__user)
        now = location_service.get_current_datetime()
        return self.get_week_for_date(date(now.year, now.month, now.day))
