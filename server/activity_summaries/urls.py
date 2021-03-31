from django.conf.urls import url

from .views import DateRangeSummaryView
from .views import DaySummaryView
from .views import DaySummaryUpdateView
from .views import ActivitySummaryView

urlpatterns = [
    url(r'summary/update/(?P<day>[\w\-]+)', DaySummaryUpdateView.as_view(), name='activity-summary-day-update'),
    url(r'summary/(?P<start>[\w\-]+)/(?P<end>[\w\-]+)', DateRangeSummaryView.as_view(), name='activity-summary-date-range'),
    url(r'summary/(?P<day>[\w\-]+)', DaySummaryView.as_view(), name='activity-summary-day'),
    url(r'summary', ActivitySummaryView.as_view(), name='activity-summary')
]
