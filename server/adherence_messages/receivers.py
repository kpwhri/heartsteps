from datetime import date
from datetime import timedelta

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.template.loader import render_to_string
from django.utils import timezone

from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccountUser
from page_views.models import PageView
from participants.signals import initialize_participant

from .models import AdherenceAlert
from .models import AdherenceMetric
from .models import Configuration
from .models import User
from .signals import send_adherence_message as send_adherence_message_signal
from .signals import update_adherence as update_adherence_signal
from .signals import update_adherence_alert as update_adherence_alert_signal
from .tasks import initialize_adherence

@receiver(initialize_participant, sender=User)
def enable_configuration(sender, user, *args, **kwargs):
    Configuration.objects.update_or_create(
        user = user,
        defaults = {
            'enabled': True
        }
    )

@receiver(pre_save, sender=Configuration)
def pre_save(sender, instance, *args, **kwargs):
    if instance.hour is None or instance.minute is None:
        instance.set_default_time()
    instance.update_daily_task()

@receiver(post_save, sender=Configuration)
def post_save_initialize(sender, instance, created, *args, **kwargs):
    if created:
        initialize_adherence.apply_async(
            kwargs = {
                'username': instance.user.username
            }
        )

@receiver(update_adherence_signal, sender=User)
def check_app_installed(sender, user, date, *args, **kwargs):
    service = DayService(user = user)
    end_time = service.get_end_of_day(date)
    initialized_time = user.date_joined

    if initialized_time > end_time:
        return False
    pageviews = PageView.objects.filter(
        user = user,
        time__gte = initialized_time,
        time__lte = end_time
    ).count()
    if pageviews > 0:
        AdherenceMetric.objects.update_or_create(
            user = user,
            category = AdherenceMetric.APP_INSTALLED,
            date = date,
            value = True
        )
    else:
        AdherenceMetric.objects.update_or_create(
            user = user,
            category = AdherenceMetric.APP_INSTALLED,
            date = date,
            value = False
        )

@receiver(update_adherence_alert_signal, sender=User)
def update_adherence_alert_app_installed(sender, user, *args, **kwargs):
    try:
        account_user = FitbitAccountUser.objects.get(
            user = user
        )
        account = account_user.account

        day_service = DayService(user = user)
        day_joined = day_service.get_date_at(user.date_joined)

        days_worn = FitbitDay.objects.filter(
            account = account,
            date__gte = day_joined,
            wore_fitbit = True
        ).count()
        page_view = PageView.objects.filter(
            user = user,
            time__gte = user.date_joined
        ).last()
        if days_worn >= 7:
            if not page_view:
                AdherenceAlert.objects.create(
                    user = user,
                    category = AdherenceMetric.APP_INSTALLED,
                    start = timezone.now()
                )
            else:
                try:
                    alert = AdherenceAlert.objects.get(
                        user = user,
                        category = AdherenceMetric.APP_INSTALLED
                    )
                    alert.end = timezone.now()
                    alert.save()
                except AdherenceAlert.DoesNotExist:
                    pass
        else:
            if page_view:
                try:
                    alert = AdherenceAlert.objects.get(
                        user = user,
                        category = AdherenceMetric.APP_INSTALLED
                    )
                    alert.end = timezone.now()
                    alert.save()
                except AdherenceAlert.DoesNotExist:
                    pass
    except FitbitAccountUser.DoesNotExist:
        pass

@receiver(send_adherence_message_signal, sender=AdherenceAlert)
def send_app_install_adherence_message(sender, adherence_alert, *args, **kwargs):
    if adherence_alert.category == AdherenceMetric.APP_INSTALLED:
        number_messages = len(adherence_alert.messages)
        if number_messages < 3:
            message_text = render_to_string(
                template_name = 'adherence_messages/app-installed.txt'
            )
            try:
                adherence_alert.create_message(message_text)
            except AdherenceAlert.AdherenceMessageRecentlySent:
                pass


@receiver(update_adherence_signal, sender=User)
def check_app_used(sender, user, date, *args, **kwargs):
    service = DayService(user = user)
    start_time = service.get_start_of_day(date)
    end_time = service.get_end_of_day(date)

    page_view_count = PageView.objects.filter(
        user = user,
        time__gte = start_time,
        time__lte = end_time
    ).count()

    if page_view_count > 0:
        AdherenceMetric.objects.update_or_create(
            user = user,
            category = AdherenceMetric.APP_USED,
            date = date,
            value = True
        )
    else:
        AdherenceMetric.objects.update_or_create(
            user = user,
            category = AdherenceMetric.APP_USED,
            date = date,
            value = False
        )

@receiver(update_adherence_alert_signal, sender=User)
def update_adherence_alert_app_used(sender, user, *args, **kwargs):
    try:
        current_adherence_alert = AdherenceAlert.objects.get(
            user = user,
            category = AdherenceMetric.APP_USED,
            end = None
        )
        recent_page_view = PageView.objects.filter(
            user = user,
            time__gt = current_adherence_alert.start
        ).last()
        if recent_page_view:
            current_adherence_alert.end = recent_page_view.time
            current_adherence_alert.save()
    except AdherenceAlert.DoesNotExist:
        last_page_view = PageView.objects.filter(
            user = user
        ).last()
        if last_page_view:
            difference = timezone.now() - last_page_view.time
            if difference.days >= 4:
                AdherenceAlert.objects.create(
                    user = user,
                    category = AdherenceMetric.APP_USED,
                    start = last_page_view.time
                )

@receiver(send_adherence_message_signal, sender=AdherenceAlert)
def check_to_send_adherence_message(sender, adherence_alert, *args, **kwargs):
    if adherence_alert.category == AdherenceMetric.APP_USED:
        duration = adherence_alert.duration
        number_messages = len(adherence_alert.messages)
        if duration > timedelta(days=4) and number_messages == 0:
            message_text = render_to_string(
                template_name = 'adherence_messages/app-used.txt',
                context = {
                    'study_phone_number': settings.STUDY_PHONE_NUMBER
                }
            )
            try:
                adherence_alert.create_message(message_text)
            except AdherenceAlert.AdherenceMessageRecentlySent:
                pass
