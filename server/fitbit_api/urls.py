from django.conf.urls import url

from fitapp.views import logout, update
from fitbit_api.views import authorize, authorize_process, authorize_complete

urlpatterns = [
    url(r'authorize/user/(?P<username>[\w\-]+)', authorize, name='fitbit-authorize-login'),
    url(r'authorize/process', authorize_process, name='fitbit-authorize-process'),
    url(r'authorize/complete', authorize_complete, name='fitbit-authorize-complete'),
    url(r'logout', logout, name='fitbit-logout'),
    url(r'update', update, name='fitbit-update')
]
