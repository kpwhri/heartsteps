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
                'watch_app_installed_date':
                    participant.watch_app_installed_date,
                'last_watch_app_data': participant.last_watch_app_data,
                'last_text_sent': participant.last_text_sent,
                'walking_suggestion_service_initialized_date': walking_suggestion_service_initialized_date
            })
        context['participant_list'] = participants
        return context

class InterventionSummaryView(CohortView):
    template_name = 'dashboard/intervention-summary.page.html'

    def get_intervention_decisions(self, model, users, start, end):
        query = model.objects.filter(
            user__in = users,
            time__gte = start,
            time__lte = end,
            test = False
        )
        return query.all()

    def get_walking_suggestion_decisions(self, users, start, end):
        return self.get_intervention_decisions(
            model = WalkingSuggestionDecision,
            users = users,
            start = start,
            end = end
        )

    def get_anti_sedentary_decisions(self, users, start, end):
        return self.get_intervention_decisions(
            model = AntiSedentaryDecision,
            users = users,
            start = start,
            end = end
        )

    def count_decision_messages(self, decisions):
        total = 0
        for decision in decisions:
            if decision.treated:
                total += 1
        return total

    def count_available_decisions(self, decisions):
        total = 0
        for decision in decisions:
            if decision.available:
                total += 1
        return total

    def count_unavailable_reasons(self, decisions):
        unavailable_reasons = {}
        query = UnavailableReason.objects.filter(
            decision__in = decisions
        )
        for _reason in query.all():
            if _reason.reason not in unavailable_reasons:
                unavailable_reasons[_reason.reason] = 0
            unavailable_reasons[_reason.reason] += 1
        return unavailable_reasons

    def list_unavailable_reasons(self, decisions):
        counts = self.count_unavailable_reasons(decisions)
        decisions_total = len(decisions)
        unavailable_reasons = []
        for reason, name in UnavailableReason.CHOICES:
            count = 0
            percentage = 0
            if reason in counts:
                count = counts[reason]
            if decisions_total:
                percentage = count/decisions_total
            unavailable_reasons.append({
                'name': name,
                'reason': reason,
                'count': count,
                'percentage': percentage
            })
        unavailable_reasons.sort(key = lambda x: (1-x['percentage'], x['name']))
        return unavailable_reasons

    def decision_availability(self, decisions):
        if not decisions or not len(decisions):
            return 0
        available_count = 0
        for decision in decisions:
            if decision.available:
                available_count += 1
        return available_count/len(decisions)

    def filter_decisions(self, decisions, start, end):
        _decisions = []
        for decision in decisions:
            if decision.time >= start and decision.time <= end:
                _decisions.append(decision)
        return _decisions

    def make_time_range(self, name, offset):
        return {
            'name': name,
            'offset': offset
        }

    def get_intervention_summaries(self, users):
        intervention_summaries = []
        time_ranges = [
            self.make_time_range('Last 3 days', 3),
            self.make_time_range('Last 7 days', 7),
            self.make_time_range('Last 14 days', 14),
            self.make_time_range('Last 28 days', 28)
        ]
        time_ranges.reverse()

        walking_suggestion_decisions = self.get_walking_suggestion_decisions(
            users = users,
            start = timezone.now() - timedelta(days=28),
            end = timezone.now()
        )
        anti_sedentary_decisions = self.get_anti_sedentary_decisions(
            users = users,
            start = timezone.now() - timedelta(days=28),
            end = timezone.now()
        )

        for time_range_dict in time_ranges:
            walking_suggestion_decisions = self.filter_decisions(
                decisions = walking_suggestion_decisions,
                start = timezone.now() - timedelta(days=time_range_dict['offset']),
                end = timezone.now()
            )
            anti_sedentary_decisions = self.filter_decisions(
                decisions = anti_sedentary_decisions,
                start = timezone.now() - timedelta(days=time_range_dict['offset']),
                end = timezone.now()
            )
            intervention_summaries.append({
                'title': time_range_dict['name'],
                'walking_suggestion_unavailable_reasons': self.list_unavailable_reasons(walking_suggestion_decisions),
                'walking_suggestion_messages': self.count_decision_messages(walking_suggestion_decisions),
                'walking_suggestion_decisions': len(walking_suggestion_decisions),
                'walking_suggestion_availability': self.decision_availability(walking_suggestion_decisions),
                'anti_sedentary_messages': self.count_decision_messages(anti_sedentary_decisions),
                'anti_sedentary_decisions': len(anti_sedentary_decisions),
                'anti_sedentary_availability': self.decision_availability(anti_sedentary_decisions),
                'anti_sedentary_unavailable_reasons': self.list_unavailable_reasons(anti_sedentary_decisions),
            })

        intervention_summaries.reverse()
        return intervention_summaries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users = []
        for participant in self.query_participants():
            if participant.user:
                users.append(participant.user)

        context['intervention_summaries'] = self.get_intervention_summaries(
            users = users
        )

        return context

class ParticipantView(InterventionSummaryView):
    template_name = 'dashboard/participant.html'

    def test_func(self):
        results = super().test_func()
        if results:
            self.setup_participant()
            return True
        else:
            return False

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

        return context

class ParticipantInterventionSummaryView(ParticipantView):
    template_name = 'dashboard/participant-intervention-summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = []
        if self.participant.user:
            users.append(self.participant.user)
        context['intervention_summaries'] = self.get_intervention_summaries(
            users = users
        )
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
