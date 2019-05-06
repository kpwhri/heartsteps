from django.dispatch import receiver

from fitbit_api.signals import update_date
from fitbit_api.models import FitbitAccount

from fitbit_activities.tasks import update_fitbit_data

@receiver(update_date, sender=FitbitAccount)
def update(sender, fitbit_user, date, *args, **kwargs):
    update_fitbit_data.apply_async(kwargs={
        'fitbit_user': fitbit_user,
        'date_string': date
    })
