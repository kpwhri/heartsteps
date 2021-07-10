from celery import shared_task

from fitbit_api.services import FitbitClient
from fitbit_api.services import FitbitService

@shared_task
def subscribe_to_fitbit(username):
    # TODO: remove print debugging
    try:
        service = FitbitService(fitbit_user=username)
        # print('fitbit service: ', service)
        fitbit_client = FitbitClient(account=service.account)
        # print('fitbit client: ', fitbit_client)
        fitbit_client.subscriptions_update()
        if not fitbit_client.is_subscribed():
            print('fitbit_client.is_subscribed is false')
            fitbit_client.subscribe()
            print('fitbit client finished subscribing')
    except FitbitService.NoAccount:
        print('FitbitService.NoAccount exception')
        return False
        
@shared_task
def unauthorize_fitbit_account(username):
    service = FitbitService(username=username)
    client = FitbitClient(account=service.account)
    client.unsubscribe()
    client.subscriptions_update()
    service.remove_credentials()
