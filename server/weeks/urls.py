from django.conf.urls import url

from .views import WeekView

urlpatterns = [
    url(r'weeks', WeekView.as_view(), name='weeks')
]
