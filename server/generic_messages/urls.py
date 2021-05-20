from django.conf.urls import url
from .views import GenericMessagesMessageCreateView

urlpatterns = [
    url(r'', GenericMessagesMessageCreateView.as_view(), name='generic-messages-create')
]
