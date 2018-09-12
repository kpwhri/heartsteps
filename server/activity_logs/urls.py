from django.conf.urls import url
from activity_logs.views import ActivityLogsList

urlpatterns = [
    url(r'logs', ActivityLogsList.as_view(), name='activity-logs')
]
