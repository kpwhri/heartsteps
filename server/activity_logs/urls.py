from django.conf.urls import url
from activity_logs.views import ActivityLogsList, ActivityLogsDetail

urlpatterns = [
    url(r'logs/(?P<log_id>[\w\-]+)', ActivityLogsDetail.as_view(), name='activity-logs-detail'),
    url(r'logs', ActivityLogsList.as_view(), name='activity-logs-list')
]
