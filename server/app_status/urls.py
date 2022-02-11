from django.conf.urls import url
from .views import AppStatusAPIView

urlpatterns = [
    url(r'app-status', AppStatusAPIView.as_view(), name='app-status')
]
