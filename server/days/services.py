
from django.core.exceptions import ImproperlyConfigured

from .models import Day
from .models import User

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

    def get_current_timezone(self):
        pass

    def get__current_date(self):
        pass

    def get_current_datetime(self):
        pass

    def get_timezone_at(self, datetime):
        pass

    def get_datetime_at(self, datetime):
        pass

    def get_date_at(self, datetime):
        pass
