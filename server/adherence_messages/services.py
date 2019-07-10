from datetime import timedelta

from django.template.loader import render_to_string

from days.services import DayService
from page_views.models import PageView

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
    
    def update_adherence(self, date = None):
        if not date:
            service = DayService(user = self.__user)
            date = service.get_current_date()
        update_adherence_signal.send(
            sender = User,
            user = self.__user,
            date = date
        )
        
    def update_app_installed(self, adherence_day):
        DailyAdherenceMetric.objects.update_or_create(
            adherence_day = adherence_day,
            category = DailyAdherenceMetric.APP_INSTALLED,
            defaults = {
                'value': self.check_app_installed(adherence_day.date)
            }
        )

    def update_app_used(self, adherence_day):
        DailyAdherenceMetric.objects.update_or_create(
            adherence_day = adherence_day,
            category = DailyAdherenceMetric.APP_USED,
            defaults = {
                'value': self.check_app_used(adherence_day.date)
            }
        )

    def send_adherence_message(self, date=None):
        self.send_message()

    def send_message(self, date=None):
        if not date:
            service = DayService(user = self.__user)
            date = service.get_current_date()

        wore_fitbit_count = AdherenceMetric.objects.filter(
            user = self.__user,
            category = AdherenceMetric.WORE_FITBIT,
            value = True
        ).count()
        app_installed_count = AdherenceMetric.objects.filter(
            user = self.__user,
            category = AdherenceMetric.APP_INSTALLED,
            value = True
        ).count()

        if wore_fitbit_count >= 7 and not app_installed_count:
            adherence_messages_sent = AdherenceMessage.objects.filter(
                user = self.__user,
                category = AdherenceMetric.APP_INSTALLED,
                created__gt = self.__user.date_joined
            ).count()
            if adherence_messages_sent < 3:
                message = self.create_message(AdherenceMetric.APP_INSTALLED, date)
                message.send()
        
        last_used = AdherenceMetric.objects.order_by('date').filter(
            user = self.__user,
            category = AdherenceMetric.APP_USED,
            value = True
        ).last()
        if not last_used:
            last_used_date = service.get_date_at(self.__user.date_joined)
        else:
            last_used_date = last_used.date

        if (date - last_used_date).days >= 4:
            last_message_threshold = service.get_end_of_day(last_used_date)
            sent_messages = AdherenceMessage.objects.filter(
                user = self.__user,
                category = AdherenceMetric.APP_USED,
                created__gte = last_message_threshold
            ).count()
            if not sent_messages:
                message = self.create_message(AdherenceMetric.APP_USED, date)
                message.send()


    def create_message(self, category, date):
        body = self.get_message_text_for(category)
        return AdherenceMessage.objects.create(
            user = self.__user,
            category = category,
            body = body,
            date = date
        )

    def get_message_text_for(self, category):
        template = 'adherence_messages/%s.txt' % (category)
        return render_to_string(template)