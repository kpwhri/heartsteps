from django.conf.urls import url
from activity_plans.views import ActivityPlansList

urlpatterns = [
    url(r'plans', ActivityPlansList.as_view(), name='activity-plans')
]
