from django.conf.urls import url
from fitbit_api.views import authorize, authorize_redirect, authorize_process, authorize_complete

urlpatterns = [
    url(r'authorize/user/(?P<username>[\w\-]+)', authorize, name='fitbit-authorize-login'),
    url(r'authorize/redirect', authorize_process, name='fitbit-authorize-redirect'),
    url(r'authorize/process', authorize_process, name='fitbit-authorize-process'),
    url(r'authorize/complete', authorize_complete, name='fitbit-authorize-complete')
]
