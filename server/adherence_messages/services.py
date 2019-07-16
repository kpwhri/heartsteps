from datetime import timedelta

from days.services import DayService
from page_views.models import PageView

from .models import AdherenceAlert
from .models import AdherenceMessage
from .models import AdherenceMetric
from .models import Configuration
from .models import User
from .signals import update_adherence as update_adherence_signal

class AdherenceService:

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

    def initialize(self):
        day_service = DayService(user = self.__user)
        start_date = day_service.get_date_at(self.__user.date_joined)
        end_date = day_service.get_current_date()
        difference = (end_date - start_date).days
        dates_to_update = [end_date - timedelta(days=offset) for offset in range(difference)]
        dates_to_update.reverse()
        for date in dates_to_update:
            self.update_adherence(date)
    
    def update_adherence(self, date = None):
        if not date:
            service = DayService(user = self.__user)
            date = service.get_current_date()
        update_adherence_signal.send(
            sender = User,
            user = self.__user,
            date = date
        )

    def get_current_adherence_alerts(self):
        alerts = AdherenceAlert.objects.order_by('start').filter(
            user = self.__user,
            end = None
        ).all()
        return list(alerts)

    def send_adherence_message(self):
        for alert in self.get_current_adherence_alerts():
            alert.send_adherence_message()
