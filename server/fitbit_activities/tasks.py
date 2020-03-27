from celery import shared_task
from datetime import timedelta
from django.utils import timezone

from fitbit_api.services import FitbitClient

from .models import FitbitAccount
from .models import FitbitDay
from .services import FitbitActivityService


@shared_task
def update_fitbit_data(fitbit_user, date_string):
    service = FitbitActivityService(
        fitbit_user = fitbit_user,
    )
    service.update_devices()
    date = service.parse_date(date_string)
    service.update(date)

@shared_task
def update_incomplete_days(fitbit_user):
    try:
        service = FitbitActivityService(
            fitbit_user = fitbit_user
        )
        query = FitbitDay.objects.filter(
            account = service.account,
            completely_updated = False
        ).order_by('date')
        for day in query.all():
            day.update(day.date)
    except FitbitClient.TooManyRequests:
        update_incomplete_days.apply_async(
            eta = timezone.now() + timedelta(minutes=90),
            kwargs = {
                'fitbit_user': fitbit_user
            }
        )

@shared_task
def update_all_fitbit_data(fitbit_user):
    service = FitbitAccount(fitbit_user = fitbit_user)
    FitbitDay.objects.filter(
        account = account
    ).update(
        completely_updated = False
    )
    update_incomplete_days.apply_async(kwargs={
        'fitbit_user': fitbit_user
    })
