from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from contact.models import ContactInformation
from fitbit_activities.models import FitbitActivity, FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from participants.models import Participant
from sms_service.forms import SendSMSForm
from sms_service.views import SendSmsCreateView

from .models import AdherenceAppInstallDashboard
from .models import FitbitServiceDashboard


class DashboardListView(UserPassesTestMixin, TemplateView):

    # Remnants of ListView
    # model = Participant
    # queryset = Participant.objects.all().prefetch_related(
    #     'user').order_by('heartsteps_id')
    template_name = 'dashboard/index.html'

    def get_login_url(self):
        return reverse('login')

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
            try:
                phone_number = participant.user.contactinformation.phone_e164
            except (AttributeError, ObjectDoesNotExist):
                phone_number = None

            try:
                first_page_view = participant.user.pageview_set.all() \
                    .aggregate(models.Max('time'))['time__max']
            except AttributeError:
                first_page_view = None

            # fitbit_service = FitbitServiceDashboard(user=participant.user)
            participants.append({
                'heartsteps_id': participant.heartsteps_id,
                'enrollment_token': participant.enrollment_token,
                'birth_year': participant.birth_year,
                'phone_number': phone_number,
                'days_wore_fitbit': adherence_app_install.days_wore_fitbit,
                'fitbit_first_updated': participant.fitbit_first_updated,
                'fitbit_last_updated': participant.fitbit_last_updated,
                'fitbit_authorized': participant.fitbit_authorized,
                'is_active': participant.is_active,
                'date_joined': participant.date_joined,
                'first_page_view': first_page_view,
                'last_page_view': participant.last_page_view,
                'watch_app_installed_date': participant.watch_app_installed_date,
                'last_watch_app_data': participant.last_watch_app_data
            })
        context['participant_list'] = participants
        return context

    def post(self, request, *args, **kwargs):
        return SendSmsCreateView.as_view()(request)
