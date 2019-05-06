from django.conf.urls import url
from .views import date_range_summary, day_summary, day_summary_update

urlpatterns = [
    url(r'summary/update/(?P<day>[\w\-]+)', day_summary_update, name='activity-summary-day-update'),
    url(r'summary/(?P<start>[\w\-]+)/(?P<end>[\w\-]+)', date_range_summary, name='activity-summary-date-range'),
    url(r'summary/(?P<day>[\w\-]+)', day_summary, name='activity-summary-day')
]
