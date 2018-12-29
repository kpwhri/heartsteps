from django.conf.urls import url

from .views import WeekView, NextWeekView

urlpatterns = [
    url(r'weeks/current', WeekView.as_view(), name='weeks-current'),
    url(r'weeks/(?P<week_id>[\w\-]+)/next', NextWeekView.as_view(), name='weeks-next'),
    url(r'weeks/(?P<week_id>[\w\-]+)', WeekView.as_view(), name='weeks-next')
]
