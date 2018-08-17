from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'device', views.DeviceView.as_view(), name='messages-device'),
    url(r'recieved', views.RecievedMessageView.as_view(), name='messages-recieved')
]
