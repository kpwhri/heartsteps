from django.conf.urls import url

from .views import UserLogsList

urlpatterns = [
    url(r'userlogs', UserLogsList.as_view(), name='user-logs-list'),
]
