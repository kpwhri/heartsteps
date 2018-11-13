from django.conf.urls import url
from fitbit_api.views import fitbit_account, fitbit_subscription

urlpatterns = [
    url(r'account', fitbit_account, name='fitbit-account'),
    url(r'subscription', fitbit_subscription, name='fitbit-subscription')
]
