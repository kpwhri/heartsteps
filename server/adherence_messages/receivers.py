from datetime import date

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from days.services import DayService
from page_views.models import PageView
from participants.signals import initialize_participant

from .models import AdherenceMetric
from .models import Configuration
from .models import User
from .signals import update_adherence as update_adherence_signal
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
