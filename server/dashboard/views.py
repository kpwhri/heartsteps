from datetime import date
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
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage as PaginatorEmptyPage
from django.core.paginator import PageNotAnInteger as PatinatorPageNotAnInteger

from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from adherence_messages.models import AdherenceMetric
from adherence_messages.services import AdherenceService
from anti_sedentary.models import AntiSedentaryDecision
from contact.models import ContactInformation
from fitbit_activities.models import FitbitActivity, FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from fitbit_api.tasks import unauthorize_fitbit_account
from participants.models import Cohort
from participants.models import Participant
from participants.models import Study
from participants.services import ParticipantService
from push_messages.services import PushMessageService
from randomization.models import UnavailableReason
from sms_messages.services import SMSService
from sms_messages.models import Contact as SMSContact
from sms_messages.models import Message as SMSMessage
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
            .filter(
                archived = False,
                cohort = self.cohort,
            )\
            .order_by('heartsteps_id')\
            .prefetch_related('user')

    # Add the Twilio from-number for the form
    def get_context_data(self, **kwargs):
        context = super(DashboardListView, self).get_context_data(**kwargs)
        participants = []
        for participant in self.query_participants():
            participants.append({
                'adherence_status': participant.adherence_status(),
                'adherence_messages': participant.recent_adherence_messages,
                'heartsteps_id': participant.heartsteps_id,
                'phone_number': participant.phone_number,
                'days_wore_fitbit': participant.fitbit_days_worn,
                'fitbit_first_updated': participant.fitbit_first_updated,
                'fitbit_last_updated': participant.fitbit_last_updated,
                'fitbit_authorized': participant.fitbit_authorized,
                'date_joined': participant.date_joined,
                'first_page_view': participant.first_page_view,
                'last_page_view': participant.last_page_view,
                'morning_messages_enabled': participant.morning_messages_enabled,
                'last_morning_message_survey_completed': participant.date_last_morning_message_survey_completed,
                'watch_app_installed_date': participant.watch_app_installed_date,
                'last_watch_app_data': participant.last_watch_app_data,
                'last_text_sent': participant.last_text_sent,
                'anti_sedentary_suggestions_enabled': participant.anti_sedentary_suggestions_enabled,
                'last_anti_sedentary_suggestion_datetime': participant.last_anti_sedentary_suggestion_datetime,
                'walking_suggestions_enabled': participant.walking_suggestions_enabled,
                'last_walking_suggestion_datetime': participant.last_walking_suggestion_datetime,
                'walking_suggestion_service_initialized_date': participant.walking_suggestion_service_initialized_date
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

class MessagesReceivedView(CohortView):
    template_name = 'dashboard/messages-received.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        participants = self.query_participants()
        users = [p.user for p in participants if p.user]
        contacts = SMSContact.objects.filter(
            user__in=users
        ).all()
        numbers = [c.number for c in contacts if c.number]

        messages = []
        sms_messages_list = SMSMessage.objects.filter(
            sender__in = numbers
        ) \
        .order_by('-created') \
        .all()

        paginator = Paginator(sms_messages_list, 50)
        page = int(self.request.GET.get('page', 1))
        try:
            sms_messages = paginator.page(page)
        except PaginatorEmptyPage:
            page = paginator.num_pages
            sms_messages = paginator.page(paginator.page)
        if page + 1 < paginator.num_pages:
            context['next_page'] = page + 1
        if page > 1:
            context['prev_page'] = page - 1

        for sms_message in sms_messages:
            heartsteps_id = None
            for c in contacts:
                if c.number == sms_message.sender:
                    for p in participants:
                        if p.user == c.user:
                            heartsteps_id = p.heartsteps_id
            if heartsteps_id and '@' in heartsteps_id:
                continue
            messages.append({
                'created': sms_message.created,
                'body': sms_message.body,
                'heartsteps_id': heartsteps_id
            })

        context['sms_messages'] = messages
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

        adherence_messages_enabled = AdherenceMessageConfiguration.objects.filter(
            user = self.participant.user,
            enabled = True
        ).count()

        context['fitbit_authorized'] = self.participant.fitbit_authorized
        context['fitbit_last_updated'] = self.participant.fitbit_last_updated

        context['configurations'] = [
            {
                'title': 'Adherence Message',
                'enabled': adherence_messages_enabled,
                'url': reverse(
                    'dashboard-cohort-participant-adherence-messages',
                    kwargs = {
                        'cohort_id':self.cohort.id,
                        'participant_id': self.participant.heartsteps_id
                    }
                )
            },
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

    template_name = 'dashboard/participant-notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = DashboardParticipant.notifications.filter(user=self.participant.user).get_notifications(
            timezone.now() - timedelta(days=7),
            timezone.now()
        )
        return context

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

class ParticipantFeatureToggleView(ParticipantView):
    template_name = 'dashboard/participant-feature-toggle.html'

    def redirect(self, request):
        return HttpResponseRedirect(
            reverse(
                'dashboard-cohort-participant',
                kwargs = {
                    'participant_id': self.participant.heartsteps_id,
                    'cohort_id':self.cohort.id
                }
            )
        )

    def add_success_message(self, request, message):
        messages.add_message(
            request,
            messages.SUCCESS,
            message
        )

    def add_error_message(self, request, message):
        messages.add_message(
            request,
            messages.ERROR,
            message
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Default Title'
        context['action'] = 'Toggle featrue'
        return context

    def post(self, request, *args, **kwargs):
        self.add_error_message(request, 'Not implemented')
        return self.redirect(request)

class ParticipantToggleAdherenceMessagesView(ParticipantFeatureToggleView):

    def is_configuration_enabled(self):
        if not self.participant.user:
            return False
        try:
            configuration = AdherenceMessageConfiguration.objects.get(
                user = self.participant.user
            )
            return configuration.enabled
        except AdherenceMessageConfiguration.DoesNotExist:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Configure Adherence Messages'

        if self.is_configuration_enabled():
            context['action'] = 'Disable Adherence Messages'
        else:
            context['action'] = 'Enable Adherence Messages'
        return context

    def post(self, request, *args, **kwargs):
        if not self.participant.user:
            self.add_error_message(request, 'Participant has no user')
            return self.redirect(request)
        if self.is_configuration_enabled():
            config = AdherenceMessageConfiguration.objects.get(
                user = self.participant.user
            )
            config.enabled = False
            config.save()
            self.add_success_message(request, 'Disabled adherence messages')
        else:
            config, _ = AdherenceMessageConfiguration.objects.get_or_create(
                user = self.participant.user
            )
            config.enabled = True
            config.save()
            self.add_success_message(request, 'Disabled adherence messages')
        return self.redirect(request)

class ParticipantDisableFitbitAccountView(ParticipantFeatureToggleView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Disable Fitbit Account'
        context['action'] = 'Disable Fitbit'
        return context

    def post(self, request, *args, **kwargs):
        if self.participant.user:
            unauthorize_fitbit_account(self.participant.user)
            self.add_success_message(request, 'Unauthorized fitbit account')
        else:
            self.add_error_message(request, 'No enrolled participant')
        return self.redirect(request)
            

class ParticipantArchiveView(ParticipantFeatureToggleView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Archive %s' % (self.participant.heartsteps_id)
        context['action'] = 'Archive Participant'
        return context

    def post(self, request, *args, **kwargs):
        self.participant.archived = True
        self.participant.save()
        self.add_success_message(request, 'Participant archived')
        return self.redirect(request)

class ParticipantUnarchiveView(ParticipantFeatureToggleView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Unarchive %s' % (self.participant.heartsteps_id)
        context['action'] = 'Unarchive Participant'
        return context

    def post(self, request, *args, **kwargs):
        self.participant.archived = False
        self.participant.save()
        self.add_success_message(request, 'Participant unarchived')
        return self.redirect(request)


class ParticipantDisableView(ParticipantFeatureToggleView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Disable %s' % (self.participant.heartsteps_id)
        context['action'] = 'Disable Participant'
        return context

    def post(self, request, *args, **kwargs):
        service = ParticipantService(
            participant=self.participant
        )
        service.disable()
        self.add_success_message(request, 'Disabled %s' % (self.participant.user.username))
        return self.redirect(request)

class ParticipantEnableView(ParticipantFeatureToggleView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Enable %s' % (self.participant.heartsteps_id)
        context['action'] = 'Enable Participant'
        return context

    def post(self, request, *args, **kwargs):
        service = ParticipantService(
            participant=self.participant
        )
        service.enable()
        self.add_success_message(
            request,
            'Enabled %s' % (self.participant.user.username)
            )
        return self.redirect(request)

class ParticipantAdherenceView(ParticipantView):

    template_name = 'dashboard/participant-adherence.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        adherence_summaries = self.participant.get_adherence_during(
            start = date.today() - timedelta(days=14),
            end = date.today()
        )
        metric_names = []
        metric_categories = []
        for category, title in AdherenceMetric.ADHERENCE_METRIC_CHOICES:
            metric_names.append(title)
            metric_categories.append(category)

        for summary in adherence_summaries:
            ordered_metrics = []
            for category in metric_categories:
                if category in summary['metrics']:
                    ordered_metrics.append(summary['metrics'][category])
                else:
                    ordered_metrics.append(False)
            summary['ordered_metrics'] = ordered_metrics
        
        context['metric_names'] = metric_names
        context['adherence_summaries'] = adherence_summaries
        return context
