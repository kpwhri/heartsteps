from django.conf.urls import url
from .views import GoalsListView, GoalView

urlpatterns = [
    url(r'goals/(?P<week_id>[\w\-]+)', GoalView.as_view(), name='weekly-goal'),
    url(r'goals', GoalsListView.as_view(), name='weekly-goals-list')
]
