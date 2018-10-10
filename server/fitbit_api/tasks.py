import requests
from datetime import datetime
from celery import shared_task

from django.contrib.auth.models import User

from fitbit_api.services import FitbitClient
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
    fitbit_service = FitbitClient(account.user)
    day = fitbit_service.get_day(date_string)
    
    fitbit_service.update_steps(day)
    fitbit_service.update_activities(day)
