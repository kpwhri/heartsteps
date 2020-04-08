from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from sms_messages.views import TwilioReplyView

urlpatterns = [
    url(r'^api/walking-suggestions/times/', include('walking_suggestion_times.urls')),
    url(r'^api/walking-suggestions/', include('walking_suggestions.urls')),
    url(r'^api/walking-suggestion-survey/', include('walking_suggestion_surveys.urls')),
    url(r'^api/activity-survey/', include('activity_surveys.urls')),
    url(r'^api/anti-sedentary/', include('anti_sedentary.urls')),
    url(r'^api/activity-suggestions/', include('randomization.urls')),
    url(r'^api/activity/', include('activity_types.urls')),
    url(r'^api/activity/', include('activity_logs.urls')),
    url(r'^api/activity/', include('activity_plans.urls')),
    url(r'^api/activity/', include('activity_summaries.urls')),
    url(r'^api/fitbit/', include('fitbit_authorize.urls')),
    url(r'^api/fitbit/', include('fitbit_api.urls')),
    url(r'^api/watch-app/', include('watch_app.urls')),
    url(r'^api/surveys/', include('surveys.urls')),
    url(r'^api/', include('page_views.urls')),
    url(r'^api/', include('contact.urls')),
    url(r'^api/', include('locations.urls')),
    url(r'^api/', include('weekly_reflection.urls')),
    url(r'^api/', include('weeks.urls')),
    url(r'^api/', include('participants.urls')),
    url(r'^api/', include('morning_messages.urls')),
    url(r'^api/', include('push_messages.urls')),
    url(r'^api/', include('weather.urls')),
    url(r'^admin/', admin.site.urls),
    url(
        r'^login/$',
        auth_views.login,
        {'template_name': 'dashboard/login.html'},
        name='login'
    ),
    url(
        r'^twilio/reply',
        TwilioReplyView.as_view(),
        name = 'sms-messages-reply'
    ),
    url(r'^api-auth', include('rest_framework.urls')),
    url(r'^export/', include('data_export.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'', include('privacy_policy.urls'))
]
