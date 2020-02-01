from django.conf.urls import url
from activity_logs.views import ActivityLogsList, ActivityLogsDetail, ActivityLogSummaryView

urlpatterns = [
    url(r'logs/summary', ActivityLogSummaryView.as_view(), name='activity-logs-summary'),
    url(r'logs/(?P<log_id>[\w\-]+)', ActivityLogsDetail.as_view(), name='activity-logs-detail'),
    url(r'logs', ActivityLogsList.as_view(), name='activity-logs-list')
]
