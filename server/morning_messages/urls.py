from django.conf.urls import url

from .views import MorningMessageView

urlpatterns = [
    url(r'morning-messages/(?P<day>[\w\-]+)', MorningMessageView.as_view(), name='morning-messages-day')
]
