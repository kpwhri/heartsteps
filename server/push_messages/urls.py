from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'device', views.DeviceView.as_view(), name='messages-device'),
    url(r'messages/(?P<message_id>[\w\-]+)', views.MessageView.as_view(), name='messages-detail'),
    url(r'messages', views.RecievedMessageView.as_view(), name='messages-received'),
    url('notification_center', views.ParticipantNotificationEndpointView.as_view(), name='get-notification-endpoint'),
]
