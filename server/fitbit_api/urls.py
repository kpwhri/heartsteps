from django.conf.urls import url
from fitbit_api.views import authorize

urlpatterns = [
    url(r'authorize/(?P<username>\w+)', authorize, name='trackers-authorize')
]
