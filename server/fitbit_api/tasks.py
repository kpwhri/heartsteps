import requests
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
def update_fitbit_data(username):
    pass