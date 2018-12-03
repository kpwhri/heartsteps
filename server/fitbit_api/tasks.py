import requests
from datetime import datetime
from celery import shared_task

from django.contrib.auth.models import User

from fitbit_api.services import FitbitClient, FitbitDayService
from fitbit_api.models import FitbitAccount, FitbitSubscription

@shared_task
def subscribe_to_fitbit(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    fitbit_client = FitbitClient(user)
    if not fitbit_client.is_subscribed():
        fitbit_client.subscribe()
        

@shared_task
def update_fitbit_data(username, date_string):
    try:
        account = FitbitAccount.objects.get(user__username=username)
    except FitbitAccount.DoesNotExist:
        return False

    fitbit_day = FitbitDayService(
        user = account.user,
        date = FitbitDayService.string_to_date(date_string)
    )
    fitbit_day.update()
