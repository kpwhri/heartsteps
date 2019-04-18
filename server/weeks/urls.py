from django.conf.urls import url

from .views import WeekView, NextWeekView, SendReflectionView, WeekSurveyView

urlpatterns = [
    url(r'weeks/current/send', SendReflectionView.as_view(), name='weeks-current-send'),
    url(r'weeks/current', WeekView.as_view(), name='weeks-current'),
    url(r'weeks/next', NextWeekView.as_view(), name='weeks-next'),
    url(r'weeks/(?P<week_number>\d+)/survey', WeekSurveyView.as_view(), name='week-surveys'),
    url(r'weeks/(?P<week_number>\d+)', WeekView.as_view(), name='weeks')
]
