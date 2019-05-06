from celery import shared_task

from fitbit_api.services import FitbitClient
from fitbit_api.models import FitbitAccount, FitbitSubscription

@shared_task
def subscribe_to_fitbit(username):
    try:
        account = FitbitAccount.objects.get(fitbit_user=username)
    except FitbitAccount.DoesNotExist:
        return False
    fitbit_client = FitbitClient(account=account)
    fitbit_client.subscriptions_update()
    if not fitbit_client.is_subscribed():
        fitbit_client.subscribe()
        
