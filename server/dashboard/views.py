from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import json
from django.db import models
from django.http import Http404
from django.http import (HttpResponseRedirect, JsonResponse)
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from contact.models import ContactInformation
from fitbit_activities.models import FitbitActivity, FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from participants.models import Cohort
from participants.models import Participant
from participants.models import Study
from sms_messages.services import SMSService
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration

from .forms import (SendSMSForm, TextHistoryForm)
from .models import AdherenceAppInstallDashboard
from .models import FitbitServiceDashboard


def get_text_history(request):
    heartsteps_id = request.GET.get('heartsteps_id', None)
    participant = Participant.objects.get(heartsteps_id=heartsteps_id)
    json_serializer = json.Serializer()
    hx = json_serializer.serialize(participant.text_message_history())

    return JsonResponse(hx, safe=False)


class CohortListView(UserPassesTestMixin, TemplateView):

    template_name = 'dashboard/cohorts.html'

    def test_func(self):
        if not self.request.user:
            return False
        admin_for_studies = Study.objects.filter(admins=self.request.user)
        self.admin_for_studies = list(admin_for_studies)
        if len(self.admin_for_studies):
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cohorts'] = []
        studies = Study.objects.filter(admins=self.request.user).all()
        for cohort in Cohort.objects.filter(study__in=studies).all():
            context['cohorts'].append({
                'id': cohort.id,
                'name': cohort.name
            })
        return context

class DashboardListView(CohortListView):

    template_name = 'dashboard/index.html'

    def get_login_url(self):
        return reverse('dashboard-login')

    def test_func(self):
        result = super().test_func()
        if not result:
            return False
        try:
            cohort = Cohort.objects.get(id=self.kwargs['cohort_id'])
            self.cohort = cohort
        except Cohort.DoesNotExist:
            raise Http404()
        if self.cohort.study in self.admin_for_studies:
            return True
        else:
            return False

    def query_participants(self):
        return Participant.objects\
            .filter(cohort = self.cohort)\
            .order_by('heartsteps_id')\
            .prefetch_related('user')

    # Add the Twilio from-number for the form
    def get_context_data(self, cohort_id, **kwargs):
        context = super(DashboardListView, self).get_context_data(**kwargs)
        context['from_number'] = settings.TWILIO_PHONE_NUMBER
        context['sms_form'] = SendSMSForm

        participants = []
        for participant in self.query_participants():

            adherence_app_install = AdherenceAppInstallDashboard(
                                    user=participant.user)
            try:
                phone_number = participant.user.contactinformation.phone_e164
            except (AttributeError, ObjectDoesNotExist):
                phone_number = None

            try:
                first_page_view = participant.user.pageview_set.all() \
                    .aggregate(models.Min('time'))['time__min']
            except AttributeError:
                first_page_view = None

            walking_suggestion_service_initialized_date = None
            try:
                if participant.user:
                    configuration = WalkingSuggestionConfiguration.objects.get(
                        user=participant.user)
                    if configuration.service_initialized_date:
                        walking_suggestion_service_initialized_date = \
                            configuration.service_initialized_date.strftime(
                                '%Y-%m-%d')
            except WalkingSuggestionConfiguration.DoesNotExist:
                pass

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
                'watch_app_installed_date':
                    participant.watch_app_installed_date,
                'last_watch_app_data': participant.last_watch_app_data,
                'last_text_sent': participant.last_text_sent,
                'walking_suggestion_service_initialized_date': walking_suggestion_service_initialized_date
            })
        context['participant_list'] = participants
        return context

    def post(self, request, *args, **kwargs):
        form = SendSMSForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['to_number']
            body = form.cleaned_data['body']

            service = SMSService(phone_number=phone_number)
            service.send(body)

        return HttpResponseRedirect(reverse('dashboard-index'))
