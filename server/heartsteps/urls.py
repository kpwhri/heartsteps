from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^api/walking-suggestions/times/', include('walking_suggestion_times.urls')),
    url(r'^api/walking-suggestions/', include('walking_suggestions.urls')),
    url(r'^api/anti-sedentary/', include('anti_sedentary.urls')),
    url(r'^api/activity/', include('activity_types.urls')),
    url(r'^api/activity/', include('activity_logs.urls')),
    url(r'^api/activity/', include('activity_plans.urls')),
    url(r'^api/activity/', include('activity_summaries.urls')),
    url(r'^api/fitbit/', include('fitbit_authorize.urls')),
    url(r'^api/fitbit/', include('fitbit_api.urls')),
    url(r'^api/watch-app/', include('watch_app.urls')),
    url(r'^api/sms/', include('sms_service.urls')),
    url(r'^api/', include('page_views.urls')),
    url(r'^api/', include('contact.urls')),
    url(r'^api/', include('locations.urls')),
    url(r'^api/', include('weekly_reflection.urls')),
    url(r'^api/', include('weeks.urls')),
    url(r'^api/', include('participants.urls')),
    url(r'^api/', include('morning_messages.urls')),
    url(r'^api/', include('push_messages.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth', include('rest_framework.urls')),
    url(r'^export/', include('data_export.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'', include('privacy_policy.urls'))
]
