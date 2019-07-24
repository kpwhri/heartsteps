from datetime import timedelta

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_api.services import FitbitService
from page_views.models import PageView

from .models import Configuration
from .models import AdherenceMessage
from .models import AdherenceMetric
from .models import User

class AdherenceServiceBase:

    class AdherenceMessageRecentlySent(RuntimeError):
        pass

    class AdherenceMessageDisabled(RuntimeError):
        pass

    def __init__(self, configuration=None, user=None, username=None):
        if username:
            try:
                configuration = Configuration.objects.get(user__username=username)
            except Configuration.DoesNotExist:
                pass
        if user:
            try:
                configuration = Configuration.objects.get(user=user)
            except Configuration.DoesNotExist:
                pass
        if configuration:
            self._configuration = configuration
            self._user = configuration.user
        else:
            raise RuntimeError('configuration not set')

    def initialize(self):
        day_service = DayService(user = self._user)
        start_date = day_service.get_date_at(self._user.date_joined)
        end_date = day_service.get_current_date()
        difference = (end_date - start_date).days

        dates_to_update = [end_date - timedelta(days=offset) for offset in range(difference)]
        dates_to_update.reverse()
        for date in dates_to_update:
            self.update_adherence(date)

    def update_adherence_metric(self, category, date, adherent):
        AdherenceMetric.objects.update_or_create(
            user = self._user,
            category = category,
            date = date,
            defaults = {
                'value': adherent
            }
        )

    def mark_adherent(self, category, date):
        self.update_adherence_metric(
            category = category,
            date = date,
            adherent = True
        )

    def mark_non_adherent(self, category, date):
        self.update_adherence_metric(
            category = category,
            date = date,
            adherent = False
        )

    def _get_current_date(self):
        service = DayService(user = self._user)
        return service.get_current_date()
    
    def _get_date_joined(self):
        service = DayService(user = self._user)
        return service.get_date_at(self._user.date_joined)

    def get_message_buffer_time(self):
        if hasattr(settings, 'ADHERENCE_MESSAGE_BUFFER_HOURS'):
            buffer_hours = settings.ADHERENCE_MESSAGE_BUFFER_HOURS
            return timezone.now() - timedelta(hours=int(buffer_hours))
        else:
            raise AdherenceAlert.AdherenceMessageBufferNotSet('Message buffer not set')
    
    def create_adherence_message(self, body, category=None):
        if not self._configuration.enabled:
            raise AdherenceServiceBase.AdherenceMessageDisabled('Unable to send messages if disabled')
        
        recently_sent_message_count = AdherenceMessage.objects.filter(
            user = self._user,
            created__gte = self.get_message_buffer_time()
        ).count()
        if recently_sent_message_count > 0:
            raise AdherenceServiceBase.AdherenceMessageRecentlySent('Unable to create message')
        
        message = AdherenceMessage.objects.create(
            user = self._user,
            category = category,
            body = body
        )
        message.send()
        return message

    def try_to_create_adherence_message(self, body, category=None):
        try:
            return self.create_adherence_message(
                body = body,
                category = category
            )
        except AdherenceServiceBase.AdherenceMessageRecentlySent:
            return None

class AdherenceAppInstalled(AdherenceServiceBase):

    def update_app_installed(self, date):
        service = DayService(user = self._user)
        end_time = service.get_end_of_day(date)
        initialized_time = self._user.date_joined

        page_view_count = PageView.objects.filter(
            user = self._user,
            time__gte = initialized_time,
            time__lte = end_time
        ).count()
        if page_view_count > 0:
            self.mark_adherent(AdherenceMetric.APP_INSTALLED, date)
        else:
            self.mark_non_adherent(AdherenceMetric.APP_INSTALLED, date)

class AdherenceAppInstallMessageService(AdherenceServiceBase):

    def get_fitbit_account(self):
        try:
            service = FitbitService(user = self._user)
            return service.account
        except:
            return None

    def app_was_installed(self):
        page_view = PageView.objects.filter(
            user = self._user,
            time__gte = self._user.date_joined
        ).last()
        if page_view:
            return True
        else:
            return False

    def days_wore_fitbit(self):
        fitbit_account = self.get_fitbit_account()
        if fitbit_account:
            return FitbitDay.objects.filter(
                account = fitbit_account,
                date__gte = self._get_date_joined(),
                wore_fitbit = True
            ).count()
        else:
            return 0

    def send_app_install_message(self):
        if self.days_wore_fitbit() >= 7 and not self.app_was_installed():
            number_of_adherence_messages = AdherenceMessage.objects.filter(
                user = self._user,
                category = AdherenceMessage.APP_INSTALLED,
                created__gt = self._user.date_joined
            ).count()
            if number_of_adherence_messages < 3:
                message_text = render_to_string(
                    template_name = 'adherence_messages/app-installed.txt'
                )
                self.create_adherence_message(
                    body = message_text,
                    category = AdherenceMessage.APP_INSTALLED
                )

class AdherenceAppUsedService(AdherenceServiceBase):

    def update_app_used(self, date):
        service = DayService(user = self._user)
        start_time = service.get_start_of_day(date)
        end_time = service.get_end_of_day(date)

        page_view_count = PageView.objects.filter(
            user = self._user,
            time__gte = start_time,
            time__lte = end_time
        ).count()

        if page_view_count > 0:
            self.mark_adherent(AdherenceMetric.APP_USED, date)
        else:
            self.mark_non_adherent(AdherenceMetric.APP_USED, date)

    def send_app_use_adherence_message(self):
        last_page_view = PageView.objects.filter(
            user = self._user
        ).last()
        if last_page_view:
            messages_sent = AdherenceMessage.objects.filter(
                user = self._user,
                category = AdherenceMessage.APP_USED,
                created__gt = last_page_view.time
            ).count()
            difference = timezone.now() - last_page_view.time
            if difference.days >= 4 and messages_sent == 0:
                message_text = render_to_string(
                    template_name = 'adherence_messages/app-used.txt',
                    context = {
                        'study_phone_number': settings.STUDY_PHONE_NUMBER
                    }
                )
                self.create_adherence_message(
                    category = 'app-used',
                    body = message_text
                )

class AdherenceFitbitUpdatedService(AdherenceServiceBase):

    def update_fitbit_updated(self, date):
        fitbit_service = FitbitService(user = self._user)
        if fitbit_service.was_updated_on(date):        
            self.mark_adherent(
                category = AdherenceMetric.FITBIT_UPDATED,
                date = date
            )
        else:
            self.mark_non_adherent(
                category = AdherenceMetric.FITBIT_UPDATED,
                date = date
            )

    def last_fitbit_update_time(self):
        try:
            fitbit_service = FitbitService(user = self._user)
            return fitbit_service.last_updated_on()
        except FitbitService.AccountNeverUpdated:
            return self._user.date_joined

    def fitbit_updated_recently(self):
        last_update_time = self.last_fitbit_update_time()
        if last_update_time:
            difference = timezone.now() - last_update_time
            if difference.days < 2:
                return True
        return False

    def send_fitbit_not_updated_message(self):
        last_update_time = self.last_fitbit_update_time()
        difference = timezone.now() - last_update_time
        if difference.days >= 2: 
            messages_query = AdherenceMessage.objects.filter(
                user = self._user,
                category = AdherenceMessage.FITBIT_UPDATED
            )
            if messages_query.count() < 2:
                message_text = render_to_string(
                    template_name = 'adherence_messages/fitbit-not-updated.txt',
                    context = {
                        'study_phone_number': settings.STUDY_PHONE_NUMBER
                    }
                )
                try:
                    self.create_adherence_message(
                        category = AdherenceMessage.FITBIT_UPDATED,
                        body = message_text
                    )
                except AdherenceServiceBase.AdherenceMessageRecentlySent:
                    pass

class AdherenceFitbitWornService(AdherenceServiceBase):

    def update_fitbit_worn(self, date):
        if self.wore_fitbit_on(date):
            self.mark_adherent(
                category = AdherenceMetric.FITBIT_WORN,
                date = date
            )
        else:
            self.mark_non_adherent(
                category = AdherenceMetric.FITBIT_WORN,
                date = date
            )
    
    def wore_fitbit_on(self, date):
        fitbit_service = FitbitService(user = self._user)
        try:
            day = FitbitDay.objects.get(
                account = fitbit_service.account,
                date = date
            )
            if day.wore_fitbit:
                return True
        except FitbitDay.DoesNotExist:
            pass
        return False

    def last_fitbit_wear_time(self):
        fitbit_service = FitbitService(user = self._user)
        last_heart_rate = FitbitMinuteHeartRate.objects.order_by('time').filter(
            account = fitbit_service.account,
            heart_rate__gt = 0
        ).last()
        if last_heart_rate:
            return last_heart_rate.time
        else:
            return self._user.date_joined

    def send_fitbit_not_worn_message(self):
        fitbit_service = FitbitService(user = self._user)
        last_wear_time = self.last_fitbit_wear_time()
        difference = timezone.now() - last_wear_time
        if difference.days >= 2:
            previous_messages_query = AdherenceMessage.objects.filter(
                user = self._user,
                category = AdherenceMessage.FITBIT_WORN,
                created__gt = last_wear_time
            )
            if previous_messages_query.count() < 2:
                first_message = previous_messages_query.first()
                if first_message:
                    difference = timezone.now() - first_message.created
                    if difference.days < 2:
                        return None
                message_text = render_to_string(
                    template_name = 'adherence_messages/fitbit-not-worn.txt',
                    context = {
                        'study_phone_number': settings.STUDY_PHONE_NUMBER
                    }
                )
                self.try_to_create_adherence_message(
                    body = message_text,
                    category = AdherenceMessage.FITBIT_WORN
                )

class AdherenceService(
        AdherenceAppInstalled,
        AdherenceAppInstallMessageService,
        AdherenceAppUsedService,
        AdherenceFitbitUpdatedService,
        AdherenceFitbitWornService
    ):

    def update_adherence(self, date = None):
        if not date:
            date = self._get_current_date()
        self.update_app_installed(date)
        self.update_app_used(date)
        self.update_fitbit_updated(date)
        self.update_fitbit_worn(date) 

    def send_adherence_message(self):
        self.send_app_install_message()
        self.send_app_use_adherence_message()
        self.send_fitbit_not_updated_message()
        self.send_fitbit_not_worn_message()
