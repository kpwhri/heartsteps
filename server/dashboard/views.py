from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
# from django.db.models import Case, IntegerField, Sum, When
from django.shortcuts import render
from django.views.generic import TemplateView

from contact.models import ContactInformation
from fitbit_activities.models import FitbitActivity, FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from participants.models import Participant
from sms_service.forms import SendSMSForm
from sms_service.views import SendSmsCreateView

# from adherence_messages.services import AdherenceAppInstallMessageService
from .models import AdherenceAppInstallDashboard
# from .models import AdherenceFitbitUpdatedDashboard
from .models import FitbitServiceDashboard


class DashboardListView(UserPassesTestMixin, TemplateView):

    # model = Participant
    # queryset = Participant.objects.all().prefetch_related(
    #     'user').order_by('heartsteps_id')
    template_name = 'dashboard/index.html'

    def test_func(self):
        if not self.request.user:
            return False
        if not self.request.user.is_staff:
            return False
        return True

    # Add the Twilio from-number for the form
    def get_context_data(self, **kwargs):
        context = super(DashboardListView, self).get_context_data(**kwargs)
        context['from_number'] = settings.TWILIO_PHONE_NUMBER
        context['form'] = SendSMSForm

        participants = []
        for participant in Participant.objects.all().prefetch_related(
                                      'user').order_by('heartsteps_id'):
            adherence_app_install = AdherenceAppInstallDashboard(
                                    user=participant.user)
            fitbit_service = FitbitServiceDashboard(user=participant.user)
            participants.append({
                'heartsteps_id': participant.heartsteps_id,
                'enrollment_token': participant.enrollment_token,
                'birth_year': participant.birth_year,
                'days_wore_fitbit': adherence_app_install.days_wore_fitbit,
                'last_updated_on': fitbit_service.last_updated_on()
            })
        context['participant_list'] = participants
        return context

    def post(self, request, *args, **kwargs):
        return SendSmsCreateView.as_view()(request)
