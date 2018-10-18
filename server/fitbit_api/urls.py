from django.conf.urls import url
from fitbit_api.views import fitbit_account, fitbit_subscription, fitbit_logs

urlpatterns = [
    url(r'account', fitbit_account, name='fitbit-account'),
    url(r'subscription', fitbit_subscription, name='fitbit-subscription'),
    url(r'(?P<day>[\w\-]+)', fitbit_logs, name='fitbit-logs')
]
