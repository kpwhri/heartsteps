from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^api/messages/', include('heartsteps_messages.urls')),
    url(r'^api/activity-suggestions/', include('activity_suggestions.urls')),
    url(r'^api/', include('heartsteps_locations.urls')),
    url(r'^api/', include('heartsteps_participants.urls')),
    url(r'^api/', include('heartsteps_randomization.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'api-auth', include('rest_framework.urls')),
    url(r'^weather/', include('weather.urls'))
]
