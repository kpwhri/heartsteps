from django.conf.urls import url
from activity_plans.views import ActivityPlansList, ActivityLogsList

urlpatterns = [
    url(r'plans', ActivityPlansList.as_view(), name='activity-plans'),
    url(r'logs', ActivityLogsList.as_view(), name='activity-logs')
]
