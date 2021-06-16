from django.conf.urls import url
from .views import DailyStepGoalsList

urlpatterns = [
    #url(r'logs/(?P<log_id>[\w\-]+)', ActivityLogsDetail.as_view(), name='activity-logs-detail'),
    url(r'dailystepgoals', DailyStepGoalsList.as_view(), name='daily-step-goals-list')
]
