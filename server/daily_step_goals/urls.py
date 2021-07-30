from django.conf.urls import url
from .views import DailyStepGoalsList, NewGoal, NewGoalCalc

urlpatterns = [
    #url(r'logs/(?P<log_id>[\w\-]+)', ActivityLogsDetail.as_view(), name='activity-logs-detail'),
    url(r'dailystepgoals', DailyStepGoalsList.as_view(), name='daily-step-goals-list'),
    url(r'newgoal', NewGoal.as_view(), name='new-daily-goal'),
    url(r'newmultipliergoal', NewGoalCalc.as_view(), name='new-goal-calc')
]
