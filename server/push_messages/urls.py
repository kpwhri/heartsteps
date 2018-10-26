from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'device', views.DeviceView.as_view(), name='messages-device'),
    url(r'messages', views.RecievedMessageView.as_view(), name='messages-received')
]
