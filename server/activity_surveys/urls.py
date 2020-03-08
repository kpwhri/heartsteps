from django.conf.urls import url
from .views import ActivitySurveyTestView

urlpatterns = [
    url(r'test', ActivitySurveyTestView.as_view(), name='activity-survey-test')
]
