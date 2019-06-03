from django.dispatch import receiver
from django.db.models.signals import pre_save

from fitbit_api.signals import update_date
from fitbit_api.models import FitbitAccount

from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_activities.tasks import update_fitbit_data

@receiver(update_date, sender=FitbitAccount)
def update(sender, fitbit_user, date, *args, **kwargs):
    update_fitbit_data.apply_async(kwargs={
        'fitbit_user': fitbit_user,
        'date_string': date
    })

@receiver(pre_save, sender=FitbitDay)
def update_wore_fitbit(sender, instance, *args, **kwargs):
    instance.wore_fitbit = instance.get_wore_fitbit()
