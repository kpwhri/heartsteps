from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import CohortListView
from .views import DashboardListView
from .views import ParticipantCreateView
from .views import ParticipantView
from .views import ParticipantEditView
from .views import ParticipantSMSMessagesView
from .views import ParticipantNotificationsView

urlpatterns = [
    url(
        r'^login/$',
        auth_views.login,
        {
            'template_name': 'dashboard/login.html'
        },
        name='dashboard-login'
    ),
    url('(?P<cohort_id>[\d]+)/create', ParticipantCreateView.as_view(), name='dashboard-cohort-participant-create'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/notifications', ParticipantNotificationsView.as_view(), name='dashboard-cohort-participant-notifications'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/messages', ParticipantSMSMessagesView.as_view(), name='dashboard-cohort-participant-sms-messages'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/edit', ParticipantEditView.as_view(), name='dashboard-cohort-participant-edit'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)', ParticipantView.as_view(), name='dashboard-cohort-participant'),
    url('(?P<cohort_id>[\d]+)', DashboardListView.as_view(), name='dashboard-cohort-participants'),
    url('', CohortListView.as_view(), name='dashboard-cohorts')
]
