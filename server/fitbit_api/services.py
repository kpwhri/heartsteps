from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from fitbit import Fitbit

from fitbit_api.models import FitbitAccount, FitbitSubscription

def create_fitbit(**kwargs):
    consumer_key = None
    consumer_secret = None
    try:
        consumer_key = settings.FITAPP_CONSUMER_KEY
        consumer_secret = settings.FITAPP_CONSUMER_SECRET
    except:
        raise ImproperlyConfigured('Missing Fitbit API credentials')
    return Fitbit(consumer_key, consumer_secret, **kwargs)

def create_callback_url(request):
    complete_url = request.build_absolute_uri(reverse('fitbit-authorize-process'))
    if 'https://' not in complete_url:
        complete_url = complete_url.replace('http://', 'https://')

class FitbitClient():

    def __init__(self, user):
        try:
            self.account = FitbitAccount.objects.get(user=user)
        except FitbitAccount.DoesNotExist:
            raise ValueError("Fitbit Account doesn't exist")
        try:
            self.subscription = FitbitSubscription.objects.get(fitbit_account=self.account)
        except FitbitSubscription.DoesNotExist:
            self.subscription = FitbitSubscription.objects.create(
                fitbit_account = self.account
            )
        self.client = self.create_client()


    def create_client(self):
        return create_fitbit(**{
            'access_token': self.account.access_token,
            'refresh_token': self.account.refresh_token,
            'expires_at': self.account.expires_at,
            'refresh_cb': lambda token: self.update_token(token)
        })

    def update_token(self, token):
        self.account.access_token = token['access_token'],
        self.account.refresh_token = token['refresh_token'],
        self.account.expires_at = token['expires_at']
        self.save()

    def subscribe(self):
        if not hasattr(settings, 'FITBIT_SUBSCRIBER_ID'):
            raise ImproperlyConfigured('No FitBit Subscriber ID')
        self.client.subscribe(
            subscription_id = str(self.subscription.uuid),
            subscriber_id = settings.FITBIT_SUBSCRIBER_ID
        )
