from django.conf.urls import url
from activity_plans.views import ActivityPlansList, ActivityPlanView, ActivityPlanSummaryView

urlpatterns = [
    url(r'plans/summary', ActivityPlanSummaryView.as_view(), name='activity-plan-summary'),
    url(r'plans/(?P<plan_id>[\w\-]+)', ActivityPlanView.as_view(), name='activity-plan-detail'),
    url(r'plans', ActivityPlansList.as_view(), name='activity-plans')
]
