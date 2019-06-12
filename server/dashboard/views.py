from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Case, IntegerField, Sum, When
from django.shortcuts import render
from django.views.generic import ListView

from contact.models import ContactInformation
from fitbit_activities.models import FitbitActivity, FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from participants.models import Participant
from sms_service.forms import SendSMSForm
from sms_service.views import SendSmsCreateView


class DashboardListView(UserPassesTestMixin, ListView):

    model = Participant
    queryset = Participant.objects.all().prefetch_related('user').order_by('heartsteps_id')
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
        return context

    def post(self, request, *args, **kwargs):
        return SendSmsCreateView.as_view()(request)

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def index(request):
    participant_list = Participant.objects.all(
        ).prefetch_related('user').order_by('heartsteps_id')
    context = {'participant_list': participant_list}

    return render(request, 'dashboard/index.html', context)
