import requests
from datetime import datetime
from celery import shared_task

from django.contrib.auth.models import User

from fitbit_api.services import FitbitClient, FitbitDayService
from fitbit_api.models import FitbitAccount, FitbitSubscription

@shared_task
def subscribe_to_fitbit(username):
    try:
        account = FitbitAccount.objects.get(fitbit_user=username)
    except FitbitAccount.DoesNotExist:
        return False
    fitbit_client = FitbitClient(account=account)
    if not fitbit_client.is_subscribed():
        fitbit_client.subscribe()
        

@shared_task
def update_fitbit_data(username, date_string):
    try:
        account = FitbitAccount.objects.get(fitbit_user=username)
    except FitbitAccount.DoesNotExist:
        return False

    fitbit_day = FitbitDayService(
        account = account,
        date = FitbitDayService.string_to_date(date_string)
    )
    fitbit_day.update()
