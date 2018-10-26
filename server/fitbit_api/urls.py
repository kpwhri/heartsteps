from django.conf.urls import url
from fitbit_api.views import fitbit_account, fitbit_subscription, fitbit_day_logs, fitbit_date_range_logs

urlpatterns = [
    url(r'account', fitbit_account, name='fitbit-account'),
    url(r'subscription', fitbit_subscription, name='fitbit-subscription'),
    url(r'(?P<start>[\w\-]+)/(?P<end>[\w\-]+)', fitbit_date_range_logs, name='fitbit-date-range-logs'),
    url(r'(?P<day>[\w\-]+)', fitbit_day_logs, name='fitbit-day-log')
]
