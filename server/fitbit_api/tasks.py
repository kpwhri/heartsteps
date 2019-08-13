from celery import shared_task

from fitbit_api.services import FitbitClient
from fitbit_api.services import FitbitService

@shared_task
def subscribe_to_fitbit(username):
    try:
        service = FitbitService(username=username)
        fitbit_client = FitbitClient(account=service.account)
        fitbit_client.subscriptions_update()
        if not fitbit_client.is_subscribed():
            fitbit_client.subscribe()
    except FitbitService.NoAccount:
        return False
        
