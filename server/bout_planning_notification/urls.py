from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'first-bout-planning-time', views.FirstBoutPlanningTimeView.as_view(), name='first-bout-planning-time'),
    url(r'bout-planning/test', views.BoutPlanningSurveyTestView.as_view(), name='bout-planning-survey-test')
]
