from django.conf.urls import url
from activity_plans.views import ActivityPlansList, ActivityPlanView

urlpatterns = [
    url(r'plans/(?P<plan_id>[\w\-]+)', ActivityPlanView.as_view(), name='activity-plan-detail'),
        url(r'plans', ActivityPlansList.as_view(), name='activity-plans')
]
