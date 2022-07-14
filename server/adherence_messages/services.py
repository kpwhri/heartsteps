from datetime import timedelta

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_api.services import FitbitService
from page_views.models import PageView
from sms_messages.models import TwilioAccountInfo
from user_event_logs.models import EventLog

from .models import Configuration
from .models import AdherenceMessage
from .models import AdherenceMetric
from .models import User

class AdherenceServiceBase:

    class AdherenceMessageRecentlySent(RuntimeError):
        pass

    class AdherenceMessageDisabled(RuntimeError):
        pass

    class NoConfiguration(RuntimeError):
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
            raise AdherenceServiceBase.NoConfiguration('configuration not set')

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

    def get_throttling_rules(self):
        return [
            {
                'message_limit': 1,
                'offset_hours': 24
            },
            {
                'message_limit': 2,
                'offset_hours': 24*4
            },
            {
                'message_limit': 4,
                'offset_hours': 24*10
            }
        ]
    
    def create_adherence_message(self, body, category=None):
        if not self._configuration.enabled:
            raise AdherenceServiceBase.AdherenceMessageDisabled('Unable to send messages if disabled')
        
        for rule in self.get_throttling_rules():
            limit = rule['message_limit']
            offset_hours = rule['offset_hours']

            count = AdherenceMessage.objects.filter(
                user = self._user,
                created__gte = timezone.now() - timedelta(hours=offset_hours)
            ).count()
            if count >= limit :
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
                from participants.models import Participant, Study, Cohort
                cohort = Cohort.objects.filter(participant__user = self.user).first()
                study = cohort.study
                query = TwilioAccountInfo.objects.filter(study=study)
        
                if query.exists():
                    account_info = query.first()
                    FROM_PHONE_NUMBER = account_info.from_phone_number
                else:
                    query = TwilioAccountInfo.objects.filter(study=None)
                    
                    account_info = query.first()
                    FROM_PHONE_NUMBER = account_info.from_phone_number

                message_text = render_to_string(
                    template_name = 'adherence_messages/app-used.txt',
                    context = {
                        'study_phone_number': FROM_PHONE_NUMBER
                    }
                )
                self.create_adherence_message(
                    category = 'app-used',
                    body = message_text
                )

class AdherenceFitbitUpdatedService(AdherenceServiceBase):

    def update_fitbit_updated(self, date):
        try:
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
        except FitbitService.NoAccount:
            self.mark_non_adherent(
                category = AdherenceMetric.FITBIT_UPDATED,
                date = date
            )

    def last_fitbit_update_time(self):
        try:
            fitbit_service = FitbitService(user = self._user)
            return fitbit_service.last_updated_on()
        except (FitbitService.NoAccount, FitbitService.AccountNeverUpdated):
            return None

    def fitbit_updated_recently(self):
        last_update_time = self.last_fitbit_update_time()
        if last_update_time:
            difference = timezone.now() - last_update_time
            if difference.days < 2:
                return True
        return False

    def send_fitbit_not_updated_message(self):
        last_update_time = self.last_fitbit_update_time()
        if not last_update_time:
            last_update_time = self._user.date_joined
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
        EventLog.info(self._user, "update_fitbit_worn() is called")
        if self.wore_fitbit_on(date):
            EventLog.info(self._user, "wore_fitbit_on({}) is true".format(date))
            self.mark_adherent(
                category = AdherenceMetric.FITBIT_WORN,
                date = date
            )
            EventLog.info(self._user, "mark_adherent()")
        else:
            EventLog.info(self._user, "wore_fitbit_on({}) is false".format(date))
            self.mark_non_adherent(
                category = AdherenceMetric.FITBIT_WORN,
                date = date
            )
            EventLog.info(self._user, "mark_non_adherent()")
    
    def wore_fitbit_on(self, date):
        EventLog.info(self._user, "wore_fitbit_on(self, date) is called")
        try:
            fitbit_service = FitbitService(user = self._user)
        except FitbitService.NoAccount:
            EventLog.error(self._user, "Fitbit Account doesn't exist")    
            return False
        EventLog.info(self._user, "FitbitService is created")

        try:
            day = FitbitDay.objects.get(
                account = fitbit_service.account,
                date = date
            )
            EventLog.info(self._user, "FitbitDay is fetched: {}".format(day))
            if day.wore_fitbit:
                EventLog.info(self._user, "User wore Fitbit during the Day")
                return True
        except FitbitDay.DoesNotExist:
            EventLog.error(self._user, "Fitbit Day doesn't exist")    
        EventLog.info(self._user, "User didn't Fitbit during the Day")
        return False

    def last_fitbit_wear_time(self):
        try:
            fitbit_service = FitbitService(user = self._user)
            last_heart_rate = FitbitMinuteHeartRate.objects.order_by('time').filter(
                account = fitbit_service.account,
                heart_rate__gt = 0
            ).last()
            if last_heart_rate:
                return last_heart_rate.time
            else:
                return None
        except FitbitService.NoAccount:
            return None

    def send_fitbit_not_worn_message(self):
            last_wear_time = self.last_fitbit_wear_time()
            if last_wear_time is None:
                last_wear_time = self._user.date_joined
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
        EventLog.info(self._user, "update_adherence({}) is called".format(date))
        if not date:
            EventLog.info(self._user, "date is None")
            date = self._get_current_date()
            EventLog.info(self._user, "date is replaced with {}".format(date))
        self.update_app_installed(date)
        EventLog.info(self._user, "update_app_installed() is called".format(date))
        self.update_app_used(date)
        EventLog.info(self._user, "update_app_used() is called".format(date))
        self.update_fitbit_updated(date)
        EventLog.info(self._user, "update_fitbit_updated() is called".format(date))
        self.update_fitbit_worn(date) 
        EventLog.info(self._user, "update_fitbit_worn() is called".format(date))

    def send_adherence_message(self):
        self.send_app_install_message()
        self.send_app_use_adherence_message()
        # self.send_fitbit_not_updated_message()
        # self.send_fitbit_not_worn_message()
