from django.conf.urls import url
from fitbit_authorize.views import authorize, authorize_start, authorize_process, authorize_complete

urlpatterns = [
    url(r'authorize/generate', authorize_start, name='fitbit-authorize-start'),
    url(r'authorize/process', authorize_process, name='fitbit-authorize-process'),
    url(r'authorize/complete', authorize_complete, name='fitbit-authorize-complete'),
    url(r'authorize/(?P<token>[\w\-]+)', authorize, name='fitbit-authorize-login'),
]
