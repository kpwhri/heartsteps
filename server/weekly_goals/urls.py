from django.conf.urls import url
from .views import GoalsListView, GoalView

urlpatterns = [
    url(r'weeks/(?P<week_id>[\w\-]+)/goal', GoalView.as_view(), name='weekly-goal'),
    url(r'weeks/goals', GoalsListView.as_view(), name='weekly-goals-list')
]
