from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from fitbit import Fitbit

def create_fitbit(**kwargs):
    consumer_key = None
    consumer_secret = None
    try:
        consumer_key = settings.FITAPP_CONSUMER_KEY
        consumer_secret = settings.FITAPP_CONSUMER_SECRET
    except:
        raise ImproperlyConfigured('Missing Fitbit API credentials')
    return Fitbit(consumer_key, consumer_secret, **kwargs)
