from django.conf.urls import url
from activity_logs.views import ActivityLogsList, ActivityLogsDetail, date_range_summary, day_summary

urlpatterns = [
    url(r'summary/(?P<start>[\w\-]+)/(?P<end>[\w\-]+)', date_range_summary, name='activity-summary-date-range'),
    url(r'summary/(?P<day>[\w\-]+)', day_summary, name='activity-summary-day'),
    url(r'logs/(?P<log_id>[\w\-]+)', ActivityLogsDetail.as_view(), name='activity-logs-detail'),
    url(r'logs/', ActivityLogsList.as_view(), name='activity-logs-list')
]
