from days.services import DayService
from page_views.models import PageView

from .models import AdherenceDay
from .models import DailyAdherenceMetric
from .models import Configuration
from .models import User

class DailyAdherenceService:

    def __init__(self, configuration=None, user=None, username=None):
        if username:
            try:
                configuration = Configuration.objects.get(user__username=username)
            except Configuration.DoesNotExist:
                raise RuntimeError('No configuration for username' % (username))
        if user:
            try:
                configuration = Configuration.objects.get(user=user)
            except Configuration.DoesNotExist:
                raise RuntimeError('No configuration for user')
        if configuration:
            self.__configuration = configuration
            self.__user = configuration.user
        else:
            raise RuntimeError('configuration not set')
    
    def update_adherence(self, date = None):
        if not date:
            service = DayService(user = self.__user)
            date = service.get_current_date()
        adherence_day, _ = AdherenceDay.objects.get_or_create(
            user = self.__user,
            date = date
        )
        self.update_app_installed(adherence_day)
        
    def update_app_installed(self, adherence_day):
        DailyAdherenceMetric.objects.update_or_create(
            adherence_day = adherence_day,
            category = DailyAdherenceMetric.APP_INSTALLED,
            defaults = {
                'value': self.check_app_installed(adherence_day.date)
            }
        )

    def check_app_installed(self, date):
        service = DayService(user = self.__user)
        end_time = service.get_end_of_day(date)
        initialized_time = self.__user.date_joined

        if initialized_time > end_time:
            return False
        pageviews = PageView.objects.filter(
            user = self.__user,
            time__gte = initialized_time,
            time__lte = end_time
        ).count()
        if pageviews > 0:
            return True
        else:
            return False

    def get_adherence(self, date = None):
        pass
