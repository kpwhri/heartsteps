from django.conf.urls import url
from fitbit_api.views import fitbit_account, fitbit_subscription, authorize, authorize_start, authorize_process, authorize_complete

urlpatterns = [
    url(r'account', fitbit_account, name='fitbit-account'),
    url(r'subscription', fitbit_subscription, name='fitbit-subscription'),
    url(r'authorize/generate', authorize_start, name='fitbit-authorize-start'),
    url(r'authorize/process', authorize_process, name='fitbit-authorize-process'),
    url(r'authorize/complete', authorize_complete, name='fitbit-authorize-complete'),
    url(r'authorize/(?P<token>[\w\-]+)', authorize, name='fitbit-authorize-login'),
]
