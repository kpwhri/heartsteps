from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import CohortListView
from .views import DashboardListView
from .views import InterventionSummaryView
from .views import ParticipantCreateView
from .views import ParticipantView
from .views import ParticipantAdherenceView
from .views import ParticipantEditView
from .views import ParticipantSMSMessagesView
from .views import ParticipantNotificationsView
from .views import ParticipantInterventionSummaryView
from .views import ParticipantEnableView
from .views import ParticipantDisableView
from .views import ParticipantArchiveView

urlpatterns = [
    url(
        r'^login/$',
        auth_views.login,
        {
            'template_name': 'dashboard/login.html'
        },
        name='dashboard-login'
    ),
    url('(?P<cohort_id>[\d]+)/intervention-summary', InterventionSummaryView.as_view(), name='dashboard-cohort-intervention-summary'),
    url('(?P<cohort_id>[\d]+)/create', ParticipantCreateView.as_view(), name='dashboard-cohort-participant-create'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/enable', ParticipantEnableView.as_view(), name='dashboard-cohort-participant-enable'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/disable', ParticipantDisableView.as_view(), name='dashboard-cohort-participant-disable'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/archive', ParticipantArchiveView.as_view(), name='dashboard-cohort-participant-archive'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/adherence', ParticipantAdherenceView.as_view(), name='dashboard-cohort-participant-adherence'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/intervention-summary', ParticipantInterventionSummaryView.as_view(), name='dashboard-cohort-participant-intervention-summary'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/notifications', ParticipantNotificationsView.as_view(), name='dashboard-cohort-participant-notifications'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/messages', ParticipantSMSMessagesView.as_view(), name='dashboard-cohort-participant-sms-messages'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/edit', ParticipantEditView.as_view(), name='dashboard-cohort-participant-edit'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)', ParticipantView.as_view(), name='dashboard-cohort-participant'),
    url('(?P<cohort_id>[\d]+)', DashboardListView.as_view(), name='dashboard-cohort-participants'),
    url('', CohortListView.as_view(), name='dashboard-cohorts')
]
