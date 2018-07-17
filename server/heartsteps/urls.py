from django.conf.urls import url, include
from django.contrib import admin

from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

urlpatterns = [
    url(r'^api/devices?$', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
    url(r'^api/messages/', include('heartsteps_messages.urls')),
    url(r'^api/', include('heartsteps_locations.urls')),
    url(r'^api/', include('heartsteps_participants.urls')),
    url(r'^api/', include('heartsteps_randomization.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'api-auth', include('rest_framework.urls'))
]
