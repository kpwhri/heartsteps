from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^api/', include('push_messages.urls')),
    url(r'^api/walking-suggestions/times/', include('walking_suggestion_times.urls')),
    url(r'^api/walking-suggestions/', include('walking_suggestions.urls')),
    url(r'^api/activity/', include('activity_types.urls')),
    url(r'^api/activity/', include('activity_logs.urls')),
    url(r'^api/activity/', include('activity_plans.urls')),
    url(r'^api/', include('contact.urls')),
    url(r'^api/', include('locations.urls')),
    url(r'^api/', include('weekly_reflection.urls')),
    url(r'^api/', include('participants.urls')),
    url(r'^api/', include('anti_seds.urls')),
    url(r'^api/fitbit/', include('fitbit_authorize.urls')),
    url(r'^api/fitbit/', include('fitbit_api.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'api-auth', include('rest_framework.urls')),
]
