from datetime import timedelta

from django.template.loader import render_to_string

from days.services import DayService
from page_views.models import PageView

from .models import AdherenceDay
from .models import AdherenceMessage
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
        self.update_app_used(adherence_day)
        
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

    def update_app_used(self, adherence_day):
        DailyAdherenceMetric.objects.update_or_create(
            adherence_day = adherence_day,
            category = DailyAdherenceMetric.APP_USED,
            defaults = {
                'value': self.check_app_used(adherence_day.date)
            }
        )

    def check_app_used(self, date):
        service = DayService(user = self.__user)
        start_time = service.get_start_of_day(date)
        end_time = service.get_end_of_day(date)

        page_view_count = PageView.objects.filter(
            user = self.__user,
            time__gte = start_time,
            time__lte = end_time
        ).count()

        if page_view_count > 0:
            return True
        else:
            return False

    def send_message(self):
        wore_fitbit_count = DailyAdherenceMetric.objects.filter(
            adherence_day__user = self.__user,
            category = DailyAdherenceMetric.WORE_FITBIT,
            value = True
        ).count()
        app_installed_count = DailyAdherenceMetric.objects.filter(
            adherence_day__user = self.__user,
            category = DailyAdherenceMetric.APP_INSTALLED,
            value = True
        ).count()

        if wore_fitbit_count >= 7 and not app_installed_count:
            adherence_messages_sent = AdherenceMessage.objects.filter(
                user = self.__user,
                category = DailyAdherenceMetric.APP_INSTALLED,
                created__gt = self.__user.date_joined
            ).count()
            if adherence_messages_sent < 3:
                message = self.create_message(DailyAdherenceMetric.APP_INSTALLED)
                message.send()
        

        service = DayService(user = self.__user)
        date = service.get_current_date()
        
        last_used = DailyAdherenceMetric.objects.order_by('adherence_day__date').filter(
            adherence_day__user = self.__user,
            category = DailyAdherenceMetric.APP_USED,
            value = True
        ).last()
        if not last_used:
            last_used_date = service.get_date_at(self.__user.date_joined)
        else:
            last_used_date = last_used.adherence_day.date

        if (date - last_used_date).days >= 4:
            last_message_threshold = service.get_end_of_day(last_used_date)
            sent_messages = AdherenceMessage.objects.filter(
                user = self.__user,
                category = DailyAdherenceMetric.APP_USED,
                created__gte = last_message_threshold
            ).count()
            if not sent_messages:
                message = self.create_message(DailyAdherenceMetric.APP_USED)
                message.send()


    def create_message(self, category):
        body = self.get_message_text_for(category)
        return AdherenceMessage.objects.create(
            user = self.__user,
            category = category,
            body = body
        )

    def get_message_text_for(self, category):
        template = 'adherence_messages/%s.txt' % (category)
        return render_to_string(template)