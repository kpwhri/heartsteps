from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from anti_sedentary.models import AntiSedentaryDecision
from contact.models import ContactInformation
from fitbit_activities.models import FitbitActivity, FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from participants.models import Cohort
from participants.models import Participant
from participants.models import Study
from participants.services import ParticipantService
from push_messages.services import PushMessageService
from randomization.models import UnavailableReason
from sms_messages.services import SMSService
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.models import WalkingSuggestionDecision

from .forms import SendSMSForm
from .forms import ParticipantCreateForm
from .forms import ParticipantEditForm
from .models import AdherenceAppInstallDashboard
from .models import FitbitServiceDashboard
from .models import DashboardParticipant

class CohortListView(UserPassesTestMixin, TemplateView):

    template_name = 'dashboard/cohorts.html'

    def get_login_url(self):
        return reverse('dashboard-login')

    def test_func(self):
        if not self.request.user or self.request.user.is_anonymous():
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
        studies = []
        for study in Study.objects.filter(admins=self.request.user).all():
            cohorts = []
            for cohort in study.cohort_set.all():
                cohorts.append({
                'id': cohort.id,
                'name': cohort.name
            })
            studies.append({
                'id': study.id,
                'name': study.name,
                'cohorts': cohorts
            })
        context['studies'] = studies
        return context

class CohortView(CohortListView):

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cohort'] = {
            'id': self.cohort.id,
            'name': self.cohort.name
        }
        return context

class DashboardListView(CohortView):

    template_name = 'dashboard/index.html'

    def query_participants(self):
        return DashboardParticipant.objects\
            .filter(cohort = self.cohort)\
            .order_by('heartsteps_id')\
            .prefetch_related('user')

    # Add the Twilio from-number for the form
    def get_context_data(self, **kwargs):
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
                'morning_messages_enabled': participant.morning_messages_enabled,
                'last_morning_message_survey_completed': participant.date_last_morning_message_survey_completed,
                'watch_app_installed_date': participant.watch_app_installed_date,
                'last_watch_app_data': participant.last_watch_app_data,
                'last_text_sent': participant.last_text_sent,
                'anti_sedentary_suggestions_enabled': participant.anti_sedentary_suggestions_enabled,
                'walking_suggestions_enabled': participant.walking_suggestions_enabled,
                'walking_suggestion_service_initialized_date': walking_suggestion_service_initialized_date
            })
        context['participant_list'] = participants
        return context

class InterventionSummaryView(CohortView):
    template_name = 'dashboard/intervention-summary.page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users = []
        for participant in self.query_participants():
            if participant.user:
                users.append(participant.user)

        anti_sedentary_decisions = DashboardParticipant.summaries.get_anti_sedentary_decisions(
            users = users,
            start = timezone.now() - timedelta(days=28),
            end = timezone.now()
        )
        walking_suggestion_decisions = DashboardParticipant.summaries.get_walking_suggestions(
            users = users,
            start = timezone.now() - timedelta(days=28),
            end = timezone.now()
        )

        time_ranges = []
        for offset in [3, 7, 14, 28]:
            time_ranges.append({
                'title': 'Last %d days' % (offset),
                'walking_suggestion_summary': DashboardParticipant.summaries.summarize_walking_suggestions(
                    users = users,
                    end = timezone.now(),
                    start = timezone.now() - timedelta(days=offset),
                    decisions = walking_suggestion_decisions
                ),
                'anti_sedentary_suggestion_summary': DashboardParticipant.summaries.summarize_anti_sedentary_suggestions(
                    users = users,
                    end = timezone.now(),
                    start = timezone.now() - timedelta(days=offset),
                    decisions = anti_sedentary_decisions
                ),
                'watch_app_availability_summary': DashboardParticipant.watch_app_step_counts.summary(
                    users = users,
                    start = timezone.now() - timedelta(days=offset),
                    end = timezone.now()
                )
            })

        context['time_ranges'] = time_ranges

        return context

class ParticipantView(CohortView):
    template_name = 'dashboard/participant.html'

    def test_func(self):
        results = super().test_func()
        if results:
            self.setup_participant()
        return results

    def setup_participant(self):
        if 'participant_id' in self.kwargs:
            try:
                participant = DashboardParticipant.objects.get(heartsteps_id=self.kwargs['participant_id'])
                self.participant = participant
            except Participant.DoesNotExist:
                raise Http404('No matching participant')
        else:
            raise Http404('No participant')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participant'] = self.participant

        context['configurations'] = [
            {
                'title': 'Anti-Sedentary Suggestions',
                'enabled': self.participant.anti_sedentary_suggestions_enabled
            },
            {
                'title': 'Walking Suggestions',
                'enabled': self.participant.walking_suggestions_enabled
            },
            {
                'title': 'Morning Messages',
                'enabled': self.participant.morning_messages_enabled
            }
        ]

        return context

class ParticipantInterventionSummaryView(ParticipantView):
    template_name = 'dashboard/participant-intervention-summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users = []
        if self.participant.user:
            users.append(self.participant.user)

        anti_sedentary_decisions = DashboardParticipant.summaries.get_anti_sedentary_decisions(
            users = users,
            start = timezone.now() - timedelta(days=28),
            end = timezone.now()
        )
        walking_suggestion_decisions = DashboardParticipant.summaries.get_walking_suggestions(
            users = users,
            start = timezone.now() - timedelta(days=28),
            end = timezone.now()
        )

        time_ranges = []
        for offset in [3, 7, 14, 28]:
            time_ranges.append({
                'title': 'Last %d days' % (offset),
                'walking_suggestion_summary': DashboardParticipant.summaries.summarize_walking_suggestions(
                    users = users,
                    end = timezone.now(),
                    start = timezone.now() - timedelta(days=offset),
                    decisions = walking_suggestion_decisions
                ),
                'anti_sedentary_suggestion_summary': DashboardParticipant.summaries.summarize_anti_sedentary_suggestions(
                    users = users,
                    end = timezone.now(),
                    start = timezone.now() - timedelta(days=offset),
                    decisions = anti_sedentary_decisions
                ),
                'watch_app_availability_summary': DashboardParticipant.watch_app_step_counts.summary(
                    users = users,
                    start = timezone.now() - timedelta(days=offset),
                    end = timezone.now()
                )
            })

        context['time_ranges'] = time_ranges

        return context

class ParticipantEditView(ParticipantView):
    template_name = 'dashboard/participant-edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ParticipantEditForm(
            initial= {
                'heartsteps_id': self.participant.heartsteps_id,
                'enrollment_token': self.participant.enrollment_token,
                'birth_year': self.participant.birth_year
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        form = ParticipantEditForm(request.POST, instance = self.participant)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Updated participant %s' % (self.participant.heartsteps_id))
            return HttpResponseRedirect(
                reverse(
                    'dashboard-cohort-participant',
                    kwargs = {
                        'cohort_id':self.cohort.id,
                        'participant_id': self.participant.heartsteps_id
                    }
                )
            )
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return TemplateResponse(
                request,
                self.template_name,
                context
            )

class ParticipantCreateView(CohortView):
    template_name = 'dashboard/participant-create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ParticipantCreateForm
        return context

    def post(self, request, *args, **kwargs):
        form = ParticipantCreateForm(request.POST)
        if form.is_valid():
            participant = form.save()
            participant.cohort = self.cohort
            participant.save()
            messages.add_message(request, messages.SUCCESS, 'Created participant %s' % (participant.heartsteps_id))
            return HttpResponseRedirect(
                reverse(
                    'dashboard-cohort-participants',
                    kwargs = {
                        'cohort_id':self.cohort.id
                    }
                )
            )
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return TemplateResponse(
                request,
                self.template_name,
                context
            )

class ParticipantNotificationsView(ParticipantView):

    def post(self, request, *args, **kwargs):

        if 'message' in request.POST and request.POST['message'] is not '':
            try:
                service = PushMessageService(username=self.participant.heartsteps_id)
                service.send_notification(request.POST['message'])
                messages.add_message(request, messages.SUCCESS, 'Message sent')
            except:
                messages.add_message(request, messages.ERROR, 'Could not send message')
        else:
            messages.add_message(request, messages.ERROR, 'No message to send')
        return HttpResponseRedirect(
            reverse(
                'dashboard-cohort-participant',
                kwargs = {
                    'participant_id': self.participant.heartsteps_id,
                    'cohort_id':self.cohort.id
                }
            )
        )

class ParticipantSMSMessagesView(ParticipantView):
    
    template_name = 'dashboard/sms-messages.html'

    def test_func(self):
        results = super().test_func()
        if results:
            try:
                self.sms_service = SMSService(user = self.participant.user)
            except SMSService.UnknownContact:
                raise Http404('No contact for participant')
            return True               
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SendSMSForm()
        messages = []
        for message in self.sms_service.get_messages():
            messages.append({
                'body': message.body,
                'time': message.created,
                'sender': message.sender,
                'from_participant': False
            })
        context['sms_messages'] = messages
        return context

    def post(self, request, *args, **kwargs):
        form = SendSMSForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data['body']

            service = SMSService(user = self.participant.user)
            service.send(body)
        context = self.get_context_data()
        context['form'] = form
        return TemplateResponse(
            request,
            self.template_name,
            context
        )

class ParticipantDisableView(ParticipantView):

    def post(self, request, *args, **kwargs):
        service = ParticipantService(
            participant=self.participant
        )
        service.disable()
        messages.add_message(
            request,
            messages.SUCCESS,
            'Disabled %s' % (self.participant.user.username)
            )

        return HttpResponseRedirect(
            reverse(
                'dashboard-cohort-participant',
                kwargs = {
                    'participant_id': self.participant.heartsteps_id,
                    'cohort_id':self.cohort.id
                }
            )
        )

class ParticipantEnableView(ParticipantView):

    def post(self, request, *args, **kwargs):
        service = ParticipantService(
            participant=self.participant
        )
        service.enable()
        messages.add_message(
            request,
            messages.SUCCESS,
            'Enabled %s' % (self.participant.user.username)
            )

        return HttpResponseRedirect(
            reverse(
                'dashboard-cohort-participant',
                kwargs = {
                    'participant_id': self.participant.heartsteps_id,
                    'cohort_id':self.cohort.id
                }
            )
        )        

