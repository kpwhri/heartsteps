from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import DevFrontView, ParticipantNotificationEndpointView
from .views import DevGenericView

from .views import CohortListView
from .views import BurstPeriodSummaryView
from .views import DashboardListView
from .views import InterventionSummaryView
from .views import ParticipantCreateView
from .views import MessagesReceivedView
from .views import ParticipantView
from .views import ParticipantAdherenceView
from .views import ParticipantEditView
from .views import ParticipantSMSMessagesView
from .views import ParticipantNotificationsView
from .views import ParticipantNotificationDetailView
from .views import ParticipantInterventionSummaryView
from .views import ParticipantEnableView
from .views import ParticipantDisableView
from .views import ParticipantArchiveView
from .views import ParticipantUnarchiveView
from .views import ParticipantToggleAdherenceMessagesView
from .views import ParticipantDisableFitbitAccountView
from .views import CloseoutSummaryView
from .views import DownloadView
from .views import DataSummaryView
from .views import ParticipantActivitySummaryView
from .views import ParticipantMorningMessagesView
from .views import ParticipantExportView
from .views import DailyTaskSummaryView
from .views import ParticipantBurstPeriodView
from .views import ParticipantBurstPeriodDeleteView
from .views import CohortMorningMessagesView
from .views import CohortWalkingSuggestionSurveyView
from .views import ParticipantBurstPeriodConfigurationView
from .views import ParticipantPageViews
from .views import ParticipantSendTestWalkingSuggestionSurvey

urlpatterns = [
    url('^login/$', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='dashboard-login'),
    url('^password-reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url('^password-reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(
        '^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(success_url='dashboard-login'),
        name='password_reset_confirm'
    ),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/burst-period/(?P<burst_period_id>[\d]+)/delete', ParticipantBurstPeriodDeleteView.as_view(), name='dashboard-cohort-participant-burst-period-delete'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/burst-period/(?P<burst_period_id>[\d]+)', ParticipantBurstPeriodView.as_view(), name='dashboard-cohort-participant-burst-period'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/burst-period/configuration', ParticipantBurstPeriodConfigurationView.as_view(), name='dashboard-cohort-participant-burst-period-configuration'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/burst-period/', ParticipantBurstPeriodView.as_view(), name='dashboard-cohort-participant-burst-period'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/morning-messages', ParticipantMorningMessagesView.as_view(), name='dashboard-cohort-participant-morning-messages'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/fitbit/disable', ParticipantDisableFitbitAccountView.as_view(), name='dashboard-cohort-participant-fitbit-disable'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/enable', ParticipantEnableView.as_view(), name='dashboard-cohort-participant-enable'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/disable', ParticipantDisableView.as_view(), name='dashboard-cohort-participant-disable'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/unarchive', ParticipantUnarchiveView.as_view(), name='dashboard-cohort-participant-unarchive'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/archive', ParticipantArchiveView.as_view(), name='dashboard-cohort-participant-archive'),    
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/adherence-messages', ParticipantToggleAdherenceMessagesView.as_view(), name='dashboard-cohort-participant-adherence-messages'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/adherence', ParticipantAdherenceView.as_view(), name='dashboard-cohort-participant-adherence'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/intervention-summary', ParticipantInterventionSummaryView.as_view(), name='dashboard-cohort-participant-intervention-summary'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/notifications_api', ParticipantNotificationEndpointView.as_view(), name='dashboard-cohort-participant-notification-endpoint'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/notifications/(?P<notification_id>[\d\w\-]+)', ParticipantNotificationDetailView.as_view(), name='dashboard-cohort-participant-notification-detail'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/notifications', ParticipantNotificationsView.as_view(), name='dashboard-cohort-participant-notifications'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/messages', ParticipantSMSMessagesView.as_view(), name='dashboard-cohort-participant-sms-messages'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/activity', ParticipantActivitySummaryView.as_view(), name='dashboard-cohort-participant-activity-summary'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/page-views', ParticipantPageViews.as_view(), name='dashboard-cohort-participant-page-views'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/edit', ParticipantEditView.as_view(), name='dashboard-cohort-participant-edit'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/export', ParticipantExportView.as_view(), name='dashboard-cohort-participant-export'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)/send-walking-suggestion-survey', ParticipantSendTestWalkingSuggestionSurvey.as_view(), name='dashboard-cohort-participant-send-walking-suggestion-survey'),
    url('(?P<cohort_id>[\d]+)/walking-suggestion-surveys/(?P<start>[\d\w\-]+)/(?P<end>[\d\w\-]+)', CohortWalkingSuggestionSurveyView.as_view()),
    url('(?P<cohort_id>[\d]+)/walking-suggestion-surveys', CohortWalkingSuggestionSurveyView.as_view(), name='dashboard-cohort-walking-suggestion-surveys'),
    url('(?P<cohort_id>[\d]+)/morning-messages', CohortMorningMessagesView.as_view(), name='dashboard-cohort-morning-messages'),
    url('(?P<cohort_id>[\d]+)/daily-tasks', DailyTaskSummaryView.as_view(), name='dashboard-cohort-daily-tasks'),
    url('(?P<cohort_id>[\d]+)/burst-periods', BurstPeriodSummaryView.as_view(), name='dashboard-cohort-burst-periods'),
    url('(?P<cohort_id>[\d]+)/download', DownloadView.as_view(), name='dashboard-cohort-download'),
    url('(?P<cohort_id>[\d]+)/data-summary', DataSummaryView.as_view(), name='dashboard-cohort-data-summary'),
    url('(?P<cohort_id>[\d]+)/closeout-summary', CloseoutSummaryView.as_view(), name='dashboard-cohort-closeout-summary'),
    url('(?P<cohort_id>[\d]+)/messages-received', MessagesReceivedView.as_view(), name='dashboard-cohort-messages-received'),
    url('(?P<cohort_id>[\d]+)/intervention-summary', InterventionSummaryView.as_view(), name='dashboard-cohort-intervention-summary'),
    url('(?P<cohort_id>[\d]+)/create', ParticipantCreateView.as_view(), name='dashboard-cohort-participant-create'),
    url('(?P<cohort_id>[\d]+)/(?P<participant_id>[\d\w\-]+)', ParticipantView.as_view(), name='dashboard-cohort-participant'),
    url('(?P<cohort_id>[\d]+)', DashboardListView.as_view(), name='dashboard-cohort-participants'),
    url('dev/front', DevFrontView.as_view(), name='dashboard-dev-front'),
    url('dev/generic', DevGenericView.as_view(), name='dashboard-dev-generic'),
    url('', CohortListView.as_view(), name='dashboard-cohorts')
]
