from django.conf.urls import url, include
from django.contrib import admin

from fitapp import views
import trackers.views

urlpatterns = [
    url(r'^api/', include('push_messages.urls')),
    url(r'^api/activity-suggestions/', include('activity_suggestions.urls')),
    url(r'^api/', include('locations.urls')),
    url(r'^api/', include('participants.urls')),
    url(r'^api/', include('randomization.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'api-auth', include('rest_framework.urls')),
    url(r'^weather/', include('weather.urls')),
    url(r'^fitbit/', include('fitapp.urls')),
    url(r'^$', trackers.views.index, name='index')
]
