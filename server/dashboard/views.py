import pprint

from datetime import date
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db import IntegrityError
from django.db.models.query import Prefetch
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import UnreadablePostError
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage as PaginatorEmptyPage
from django.core.paginator import PageNotAnInteger as PatinatorPageNotAnInteger

import pytz
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from adherence_messages.models import AdherenceMetric
from adherence_messages.services import AdherenceService
from anti_sedentary.models import AntiSedentaryDecision
from burst_periods.models import Configuration as BurstPeriodConfiguration
from burst_periods.models import BurstPeriod
from closeout_messages.models import Configuration as CloseoutConfiguration
from contact.models import ContactInformation
from days.models import Day
from fitbit_clock_face.models import ClockFace
from fitbit_clock_face.models import ClockFaceLog
from fitbit_clock_face.models import StepCount
from fitbit_activities.models import FitbitActivity, FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser, FitbitAccountUpdate
from fitbit_api.tasks import unauthorize_fitbit_account
from fitbit_api.models import FitbitDevice
from generic_messages.services import GenericMessagesService
from morning_messages.models import MorningMessage
from morning_messages.models import Configuration as MorningMessageConfiguration
from participants.models import Cohort
from participants.models import Participant
from participants.models import Study
from participants.models import DataExport
from participants.models import DataExportSummary
from participants.models import DataExportQueue
from participants.services import ParticipantService
from page_views.models import PageView
from push_messages.services import PushMessageService
from push_messages.models import Device, Message as PushMessage
from randomization.models import UnavailableReason
from sms_messages.services import SMSService
from sms_messages.models import Contact as SMSContact
from sms_messages.models import Message as SMSMessage
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.models import WalkingSuggestionDecision
from walking_suggestions.models import NightlyUpdate as WalkingSuggestionNightlyUpdate
from watch_app.models import StepCount as WatchAppStepCount
from walking_suggestion_surveys.models import Configuration as WalkingSuggestionSurveyConfiguration
from walking_suggestion_surveys.models import Decision as WalkingSuggestionSurveyDecision
from walking_suggestion_surveys.models import WalkingSuggestionSurvey

from nlm.services import StudyTypeService, LogService
from nlm.models import CohortAssignment

from daily_tasks.models import DailyTask
from django_celery_results.models import TaskResult

from days.services import DayService
from user_event_logs.models import EventLog

from .forms import CohortFeatureFlagEditForm, ParticipantFeatureFlagEditForm, SendSMSForm, StudyFeatureFlagEditForm
from .forms import ParticipantCreateForm
from .forms import ParticipantEditForm
from .forms import BurstPeriodForm
from .forms import ClockFacePairForm
from .models import AdherenceAppInstallDashboard
from .models import FitbitServiceDashboard
from .models import DashboardParticipant

from .services import DevSendNotificationService
from .services import DevService


class DevFrontView(UserPassesTestMixin, TemplateView):

    template_name = 'dashboard/dev-front.html'

    def get_login_url(self):
        return reverse('dashboard-login')

    def test_func(self):
        if self.request.user and not self.request.user.is_anonymous:
            admin_for_studies = Study.objects.filter(admins=self.request.user)
            self.admin_for_studies = list(admin_for_studies)
            if self.request.user.is_staff or self.admin_for_studies:
                return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_staff"] = self.request.user.is_staff

        dev_service = DevService(self.request.user)
        nlm_service = StudyTypeService("NLM", self.request.user)

        study_query = dev_service.get_all_studies_query()
        context[
            'studies'] = dev_service.get_study_cohort_participant_device_dict(
                study_query)

        debug_studies_query = dev_service.get_all_studies_query(debug=True)
        context[
            'debug_studies'] = dev_service.get_study_cohort_participant_device_dict(
                debug_studies_query)

        colleagues = dev_service.get_colleague_dict()
        context['colleagues'] = colleagues

        participant_users = dev_service.get_participant_users_dict()
        context['participant_users'] = participant_users

        cohorts = dev_service.get_cohort_dict()
        context['cohorts'] = cohorts

        nlm_cohorts = nlm_service.get_nlm_cohorts_dict()
        context['nlmcohorts'] = nlm_cohorts
        if len(nlm_cohorts) > 0:
            context['nlmcohort_text'] = ", ".join(
                [x["name"] for x in nlm_cohorts])
        else:
            context['nlmcohort_text'] = "No cohort is NLM-style."

        hourly_tasks = dev_service.get_hourly_tasks_dict()
        context['hourly_tasks'] = hourly_tasks

        context['generic_command_list'] = [
            "insert_test_log", "dump_log", 'clear_log', 'view_crontabs',
            'view_periodic_tasks', 'view_hourly_tasks',
            'create_sample_hourly_tasks', "delete_all_hourly_tasks",
            'design_test_study', 'view_test_study', 'clear_test_study',
            'view_preloaded_seq', 'clear_preloaded_seq',
            'view_cohort_assignment'
        ]

        return context


class DevGenericView(UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/dev-message.html'

    def get_login_url(self):
        return reverse('dashboard-login')

    def test_func(self):
        if self.request.user and not self.request.user.is_anonymous:
            admin_for_studies = Study.objects.filter(admins=self.request.user)
            self.admin_for_studies = list(admin_for_studies)
            if self.request.user.is_staff or self.admin_for_studies:
                return True
        return False

    def send_notification(self, player_ids):
        dev_send_notification_service = DevSendNotificationService()
        message_response_id = dev_send_notification_service.send_dev_notification(
            device_id=player_ids)
        return "Notification is sent: {}".format(player_ids)

    def set_device_token(self, username, player_id):
        dev_send_notification_service = DevSendNotificationService()
        result = dev_send_notification_service.set_device_token(
            username, player_id)
        return "Notification is sent: {}".format(result)

    def prettyprint(self, obj):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)

        return pp.pformat(obj)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        self.dev_service = DevService(self.request.user)
        self.nlm_service = StudyTypeService("NLM", self.request.user)

        context["userstring"] = self.request.user
        context["is_superuser"] = self.request.user.is_staff

        if self.request.user and self.request.user.is_superuser:
            dev_command = request.POST['dev-command']

            if dev_command == 'send-notification':
                player_ids = [request.POST['playerid']]
                context["results"] = self.send_notification(player_ids)
            elif dev_command == 'set-device-token':
                username = request.POST['username']
                player_id = request.POST['playerid']
                context["results"] = self.set_device_token(username, player_id)
            elif dev_command == 'create-debug-study':
                number_of_studies = int(request.POST['number_of_studies'])
                context["results"] = self.dev_service.create_debug_study(
                    number_of_studies)
            elif dev_command == 'create-debug-cohort':
                number_of_cohorts = int(request.POST['number_of_cohorts'])
                context["results"] = self.dev_service.create_debug_cohort(
                    number_of_cohorts)
            elif dev_command == 'create-debug-participant':
                number_of_participants = int(
                    request.POST['number_of_participants'])
                context["results"] = self.dev_service.create_debug_participant(
                    number_of_participants)
            elif dev_command == 'clear-debug-study':
                context["results"] = self.dev_service.clear_debug_study()
            elif dev_command == 'clear-debug-participant':
                context["results"] = self.dev_service.clear_debug_participant()
            elif dev_command == 'clear-orphan-debug-participant':
                context[
                    "results"] = self.dev_service.clear_orphan_debug_participant(
                    )
            elif dev_command == 'send-notification-to-user':
                username = request.POST['username']
                user = self.dev_service.get_user_by_username(username)
                result = self.dev_service.send_notification_by_user(user)
                context["results"] = result
            elif dev_command == 'send-typed-notification-to-user':
                username = request.POST['username']
                notification_type = request.POST['notification_type']
                user = self.dev_service.get_user_by_username(username)
                result = self.dev_service.send_typed_notification_by_user(
                    user, notification_type)
                context["results"] = result
            elif dev_command == 'assign-cohort-to-nlm':
                cohort_id = request.POST['cohort-id']
                cohort = self.dev_service.get_cohort_by_id(cohort_id)
                context["results"] = self.nlm_service.assign_cohort_to_nlm(
                    cohort)
            elif dev_command == 'test_logs':
                log_service = LogService()
                log_service.log("test log")
                context["results"] = log_service.dump(pretty=True)
            elif dev_command == 'delete_hourly_tasks':
                hourly_task_id = request.POST['hourly-task-id']
                self.dev_service.delete_hourly_task_by_id(
                    hourly_task_id=hourly_task_id)
                objlist = self.dev_service.get_all_hourly_tasks()
                context["results"] = self.prettyprint(objlist)
            elif dev_command == 'upload_level_csv':
                nickname = request.POST['nickname']
                if request.FILES['level_csv_file_form_control']:
                    level_csv_file = request.FILES.get(
                        'level_csv_file_form_control')

                    if (level_csv_file.multiple_chunks()):
                        raise UnreadablePostError("too long")
                    else:
                        csv_file_content = level_csv_file.read().decode(
                            "utf-8-sig")
                        lines = csv_file_content.split("\n")
                        try:
                            context[
                                "results"] = self.nlm_service.upload_level_csv(
                                    level_csv_file.name, nickname, lines)
                        except IntegrityError:
                            context[
                                "results"] = "The nickname {} is already used.".format(
                                    nickname)
                else:
                    raise UnreadablePostError
            elif dev_command == 'generic-command':
                generic_command = request.POST['generic-command']
                if generic_command == 'delete_all_hourly_tasks':
                    self.dev_service.delete_all_hourly_tasks()
                elif generic_command == 'insert_test_log':
                    log_service = LogService()
                    log_service.log("test log")
                    context["results"] = LogService.dump(pretty=True)
                elif generic_command == 'dump_log':
                    context["results"] = LogService.dump(pretty=True)
                elif generic_command == 'clear_log':
                    context["results"] = LogService.clear_all()
                elif generic_command == 'view_crontabs':
                    crontabs = self.dev_service.get_all_crontabs()
                    context["results"] = self.prettyprint(crontabs)
                elif generic_command == 'view_periodic_tasks':
                    objlist = self.dev_service.get_all_periodic_tasks()
                    context["results"] = self.prettyprint(objlist)
                elif generic_command == 'view_hourly_tasks':
                    objlist = self.dev_service.get_all_hourly_tasks()
                    context["results"] = self.prettyprint(objlist)
                elif generic_command == 'create_sample_hourly_tasks':
                    self.dev_service.create_sample_hourly_tasks()
                    objlist = self.dev_service.get_all_hourly_tasks()
                    context["results"] = self.prettyprint(objlist)
                elif generic_command == 'design_test_study':
                    objlist = self.dev_service.design_test_study()
                    context["results"] = self.prettyprint(objlist)
                elif generic_command == 'view_test_study':
                    lines = self.dev_service.view_test_study()
                    context["results"] = "\n".join(lines)
                elif generic_command == 'clear_test_study':
                    objlist = self.dev_service.delete_test_study()
                    context["results"] = self.prettyprint(objlist)
                elif generic_command == 'view_preloaded_seq':
                    lines = self.dev_service.view_preloaded_seq()
                    context["results"] = "\n".join(lines)
                elif generic_command == 'clear_preloaded_seq':
                    objlist = self.dev_service.delete_preloaded_seq()
                    context["results"] = self.prettyprint(objlist)
                elif generic_command == 'view_cohort_assignment':
                    objlist = self.dev_service.view_generic_model(
                        [CohortAssignment])
                    context["results"] = self.prettyprint(objlist)
                else:
                    context[
                        "results"] = "Unsupported generic command: {}".format(
                            generic_command)
            else:
                context["results"] = "Unsupported command: {}".format(
                    dev_command)

            return TemplateResponse(request, self.template_name, context)
        else:
            return TemplateResponse(request, self.template_name, context)


class CohortListView(UserPassesTestMixin, TemplateView):

    template_name = 'dashboard/cohorts.html'

    def get_login_url(self):
        return reverse('dashboard-login')

    def test_func(self):
        if self.request.user and not self.request.user.is_anonymous:
            admin_for_studies = Study.objects.filter(admins=self.request.user)
            self.admin_for_studies = list(admin_for_studies)
            if self.request.user.is_staff or self.admin_for_studies:
                return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cohorts'] = []
        studies = []
        if self.request.user.is_superuser:
            study_query = Study.objects
        else:
            study_query = Study.objects.filter(admins=self.request.user)
        for study in study_query.all():
            cohorts = []
            for cohort in study.cohort_set.all():
                cohorts.append({'id': cohort.id, 'name': cohort.name})
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
        if self.request.user.is_superuser or self.cohort.study in self.admin_for_studies:
            return True
        else:
            return False

    def query_participants(self):
        return Participant.objects\
            .filter(cohort=self.cohort)\
            .order_by('heartsteps_id')\
            .prefetch_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cohort'] = self.cohort
        return context


class DashboardListView(CohortView):

    template_name = 'dashboard/index.html'

    def query_participants(self):
        return DashboardParticipant.objects\
            .filter(
                archived=False,
                cohort=self.cohort,
            )\
            .order_by('heartsteps_id')\
            .prefetch_related('user') \
            .prefetch_related('cohort')

    # Add the Twilio from-number for the form
    def get_context_data(self, **kwargs):
        context = super(DashboardListView, self).get_context_data(**kwargs)

        participants = self.query_participants() \
            .prefetch_contact_information() \
            .prefetch_fitbit_account() \
            .prefetch_clock_face_summary() \
            .prefetch_page_views()

        context['participant_list'] = participants
        return context


class DailyTaskSummaryView(CohortView):
    template_name = 'dashboard/daily-task-summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participants = self.query_participants()
        users = [p.user for p in participants if p.user]

        daily_tasks = DailyTask.objects.filter(
            user__in=users
        ).prefetch_related('task') \
            .prefetch_related('user') \
            .all()

        daily_tasks_by_username_then_task_name = {}
        for user in users:
            daily_tasks_by_username_then_task_name[user.username] = {}

        task_names = []
        for dt in daily_tasks:
            if not dt.task:
                continue
            task_name = dt.task.task
            if task_name not in task_names:
                task_names.append(task_name)
            if task_name not in daily_tasks_by_username_then_task_name[
                    dt.user.username]:
                daily_tasks_by_username_then_task_name[
                    dt.user.username][task_name] = {
                        'run_times': []
                    }
            if dt.day:
                run_time = '%s %d:%d' % (dt.day, dt.hour, dt.minute)
            else:
                run_time = '%d:%d' % (dt.hour, dt.minute)
            daily_tasks_by_username_then_task_name[
                dt.user.username][task_name]['run_times'].append(run_time)

            if dt.task.last_run_at:
                task_last_run_at = dt.task.last_run_at.astimezone(
                    pytz.timezone('US/Pacific'))
                if 'last_run_at' in daily_tasks_by_username_then_task_name[
                        dt.user.username][task_name]:
                    last_run_at = daily_tasks_by_username_then_task_name[
                        dt.user.username][task_name]['last_run_at']
                    if last_run_at < task_last_run_at:
                        daily_tasks_by_username_then_task_name[
                            dt.user.username][task_name][
                                'last_run_at'] = task_last_run_at
                else:
                    daily_tasks_by_username_then_task_name[dt.user.username][
                        task_name]['last_run_at'] = task_last_run_at

        task_names.sort()
        context['task_names'] = [
            tn.replace('.tasks.', ' ').replace('_', ' ') for tn in task_names
        ]
        serialized_participants = []
        for participant in participants:
            serialized_tasks = []
            for task in task_names:
                if participant.user:
                    username = participant.user.username
                    if username in daily_tasks_by_username_then_task_name:
                        if task in daily_tasks_by_username_then_task_name[
                                username]:
                            st = daily_tasks_by_username_then_task_name[
                                participant.user.username][task]
                            if 'last_run_at' in st:
                                st['last_run_at'] = st['last_run_at'].strftime(
                                    '%Y-%m-%d %H:%M;%S')
                            serialized_tasks.append(st)
                        else:
                            serialized_tasks.append({})
                    else:
                        serialized_tasks.append({})
                else:
                    serialized_tasks.append({})

            serialized_participants.append({
                'heartsteps_id': participant.heartsteps_id,
                'active': participant.active,
                'archived': participant.archived,
                'tasks': serialized_tasks
            })
        context['participants'] = serialized_participants
        return context


class BurstPeriodSummaryView(CohortView):
    template_name = 'dashboard/burst-period-summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participants = DashboardParticipant.objects \
            .filter(
                archived=False,
                cohort=self.cohort,
            ) \
            .order_by('heartsteps_id') \
            .prefetch_related('user') \
            .all()

        context['participants'] = [
            p for p in participants if p.burst_period_enabled
        ]
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
            users=users,
            start=timezone.now() - timedelta(days=28),
            end=timezone.now())
        walking_suggestion_decisions = DashboardParticipant.summaries.get_walking_suggestions(
            users=users,
            start=timezone.now() - timedelta(days=28),
            end=timezone.now())

        time_ranges = []
        for offset in [3, 7, 14, 28]:
            time_ranges.append({
                'title':
                'Last %d days' % (offset),
                'walking_suggestion_summary':
                DashboardParticipant.summaries.summarize_walking_suggestions(
                    users=users,
                    end=timezone.now(),
                    start=timezone.now() - timedelta(days=offset),
                    decisions=walking_suggestion_decisions),
                'anti_sedentary_suggestion_summary':
                DashboardParticipant.summaries.
                summarize_anti_sedentary_suggestions(
                    users=users,
                    end=timezone.now(),
                    start=timezone.now() - timedelta(days=offset),
                    decisions=anti_sedentary_decisions),
                'watch_app_availability_summary':
                DashboardParticipant.watch_app_step_counts.summary(
                    users=users,
                    start=timezone.now() - timedelta(days=offset),
                    end=timezone.now())
            })

        context['time_ranges'] = time_ranges

        return context


class DownloadView(CohortView):
    template_name = 'dashboard/download.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participants = self.query_participants().prefetch_related('user').all()
        users = [p.user for p in participants if p.user]
        export_summaries_by_username = {}
        categories = []
        data_export_summaries = DataExportSummary.objects.filter(user__in=users) \
            .prefetch_related('user') \
            .prefetch_related('last_data_export') \
            .all()
        for summary in data_export_summaries:
            if summary.category not in categories:
                categories.append(summary.category)
            username = summary.user.username
            if username not in export_summaries_by_username:
                export_summaries_by_username[username] = {}
            export_summaries_by_username[username][summary.category] = summary
        categories.sort()
        total_participants = 0
        total_files = 0
        total_errors = 0
        export_types = {}
        context['participants'] = []
        for _participant in participants:
            total_participants += 1
            exports = []
            for _filename in categories:
                if _participant.user:
                    username = _participant.user.username
                    if username in export_summaries_by_username and _filename in export_summaries_by_username[
                            username]:
                        summary = export_summaries_by_username[username][
                            _filename]
                        last_updated = None
                        duration = None
                        error = None
                        export = summary.last_data_export
                        if export:
                            last_updated = export.start.strftime('%Y-%m-%d')
                            duration = export.duration
                            error = export.error_message
                        exports.append({
                            'filename': summary.category,
                            'date': last_updated,
                            'duration': duration,
                            'error': error
                        })
                        if summary.category not in export_types:
                            export_types[summary.category] = {
                                'name': summary.category,
                                'count': 0,
                                'errors': 0,
                                'recent': 0
                            }
                        if export:
                            total_files += 1
                            export_types[summary.category]['count'] += 1
                            if export.error_message:
                                total_errors += 1
                                export_types[export.export_type]['errors'] += 1
                            if export.start > timezone.now() - timedelta(
                                    days=3):
                                export_types[export.export_type]['recent'] += 1
                else:
                    exports.append(None)

            status = "Disabled"
            if _participant.enabled:
                status = "Active"
            study_start = "Not started"
            if _participant.study_start_date:
                study_start = _participant.study_start_date.strftime(
                    '%Y-%m-%d')
            study_end = "No end defined"
            if _participant.study_end:
                study_end = _participant.study_end.strftime('%Y-%m-%d')
            context['participants'].append({
                'heartsteps_id': _participant.heartsteps_id,
                'status': status,
                'study_start': study_start,
                'study_end': study_end,
                'exports': exports
            })
        context['filenames'] = categories
        context['export_types'] = [export_types[_f] for _f in categories]
        context['total_participants'] = total_participants
        context['total_files'] = total_files
        context['total_errors'] = total_errors
        return context

    def post(self, request, *args, **kwargs):
        participants = self.query_participants().prefetch_related('user').all()
        users = [p.user for p in participants if p.user]
        export_count = 0
        for user in users:
            DataExportQueue.objects.create(user=user)
            export_count += 1
        messages.add_message(request, messages.SUCCESS,
                             'Queued %d data exports' % (export_count))
        return HttpResponseRedirect(
            reverse('dashboard-cohort-download',
                    kwargs={'cohort_id': self.cohort.id}))


class DataSummaryView(CohortView):
    template_name = 'dashboard/data-summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participants = self.query_participants().all()
        users = [p.user for p in participants if p.user]
        fitbit_data_by_username = {}
        fitbit_authorized_by_username = {}
        account_users = FitbitAccountUser.objects.filter(
            user__in=users).prefetch_related('user').prefetch_related(
                'account').all()
        username_by_fitbit_account = {}
        for au in account_users:
            username_by_fitbit_account[
                au.account.fitbit_user] = au.user.username
            fitbit_authorized_by_username[
                au.user.username] = au.account.authorized
        fitbit_days = FitbitDay.objects.filter(
            account__fitbit_user__in=username_by_fitbit_account.keys(),
            date__lte=date.today()).prefetch_related('account').all()
        for _day in fitbit_days:
            _username = username_by_fitbit_account[_day.account.fitbit_user]
            if _username not in fitbit_data_by_username:
                fitbit_data_by_username[_username] = {
                    'total_days': 0,
                    'total_days_worn': 0,
                    'total_days_complete': 0
                }
            fitbit_data_by_username[_username]['total_days'] += 1
            if _day.wore_fitbit:
                fitbit_data_by_username[_username]['total_days_worn'] += 1
            if _day.completely_updated:
                fitbit_data_by_username[_username]['total_days_complete'] += 1
        fitbit_devices = FitbitDevice.objects.filter(
            account__fitbit_user__in=username_by_fitbit_account.keys(
            )).prefetch_related('account').all()
        for _fitbit_device in fitbit_devices:
            _username = username_by_fitbit_account[
                _fitbit_device.account.fitbit_user]
            last_updated = _fitbit_device.last_updated
            if 'last_device_update' in fitbit_data_by_username[_username]:
                if last_updated > fitbit_data_by_username[_username][
                        'last_device_update']:
                    fitbit_data_by_username[_username][
                        'last_device_update'] = last_updated
            else:
                fitbit_data_by_username[_username][
                    'last_device_update'] = last_updated
        walking_suggestion_last_updated_by_username = {}
        nightly_updates = WalkingSuggestionNightlyUpdate.objects.filter(
            user__in=users).prefetch_related('user').all()
        for _update in nightly_updates:
            _username = _update.user.username
            walking_suggestion_last_updated_by_username[
                _username] = _update.day

        recently_updated_date = date.today() - timedelta(days=4)
        recently_updated_walking_suggestions_count = 0
        recently_updated_fitbit_data = 0

        serialized_participants = []
        for _participant in participants:
            username = None
            if _participant.user:
                username = _participant.user.username
            status = "Disabled"
            if _participant.enabled:
                status = "Active"
            study_start = "Not started"
            if _participant.study_start_date:
                study_start_date = _participant.study_start_date.strftime(
                    '%Y-%m-%d')
            fitbit_total_days = 0
            fitbit_days_worn = 0
            fitbit_days_complete = 0
            if username and username in fitbit_data_by_username:
                fitbit_days_total = fitbit_data_by_username[username][
                    'total_days']
                fitbit_days_worn = fitbit_data_by_username[username][
                    'total_days_worn']
                fitbit_days_complete = fitbit_data_by_username[username][
                    'total_days_complete']
            last_walking_suggestion_update = "None"
            if username and username in walking_suggestion_last_updated_by_username:
                last_walking_suggestion_update = walking_suggestion_last_updated_by_username[
                    username].strftime('%Y-%m-%d')
            if username and username in walking_suggestion_last_updated_by_username:
                if recently_updated_date <= walking_suggestion_last_updated_by_username[
                        username]:
                    recently_updated_walking_suggestions_count += 1
            fitbit_last_updated = None
            if username and username in fitbit_data_by_username and 'last_device_update' in fitbit_data_by_username[
                    username]:
                last_update = fitbit_data_by_username[username][
                    'last_device_update']
                try:
                    _last_fitbit_update_date = date(last_update.year,
                                                    last_update.month,
                                                    last_update.day)
                    fitbit_last_updated = _last_fitbit_update_date.strftime(
                        '%Y-%m-%d')
                    if recently_updated_date <= _last_fitbit_update_date:
                        recently_updated_fitbit_data += 1
                except ValueError as e:
                    print(e, last_update)
            fitbit_authorized = 'No account'
            if username and username in fitbit_authorized_by_username:
                if fitbit_authorized_by_username[username]:
                    fitbit_authorized = 'Authorized'
                else:
                    fitbit_authorized = 'Unauthorized'
            serialized_participants.append({
                'heartsteps_id':
                _participant.heartsteps_id,
                'status':
                status,
                'study_start':
                study_start_date,
                'fitbit_days_total':
                fitbit_days_total,
                'fitbit_days_worn':
                fitbit_days_worn,
                'fitbit_days_complete':
                fitbit_days_complete,
                'last_walking_suggestion_update':
                last_walking_suggestion_update,
                'fitbit_last_updated':
                fitbit_last_updated,
                'fitbit_authorized':
                fitbit_authorized
            })

        context['participants'] = serialized_participants
        context['total_participants'] = len(serialized_participants)
        context['recently_updated_fitbit'] = recently_updated_fitbit_data
        context[
            'recently_updated_walking_suggestion_service'] = recently_updated_walking_suggestions_count
        return context


class CloseoutSummaryView(CohortView):
    template_name = 'dashboard/closeout-summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participants = self.query_participants() \
            .exclude(user=None) \
            .all()
        participants_by_username = {}
        for _participant in participants:
            participants_by_username[_participant.user.username] = _participant

        users = [_p.user for _p in participants if _p.user]
        configurations = CloseoutConfiguration.objects \
            .prefetch_related('user') \
            .prefetch_related('message') \
            .filter(user__in=users) \
            .order_by('closeout_date') \
            .all()

        contacts = SMSContact.objects.filter(
            user__in=users).prefetch_related('user').all()
        contact_number_by_username = {}
        username_by_contact_number = {}
        for _contact in contacts:
            contact_number_by_username[
                _contact.user.username] = _contact.number
            username_by_contact_number[
                _contact.number] = _contact.user.username
        sms_message_query = None
        for _configuration in [_c for _c in configurations if _c.message]:
            if _configuration.user.username in contact_number_by_username:
                number = contact_number_by_username[
                    _configuration.user.username]
                if not sms_message_query:
                    sms_message_query = models.Q(
                        sender=number,
                        created__gt=_configuration.message.created)
                else:
                    sms_message_query = sms_message_query | models.Q(
                        sender=number,
                        created__gt=_configuration.message.created)
        usernames_that_responded = []
        if sms_message_query:
            for _sms_message in SMSMessage.objects.filter(
                    sms_message_query).all():
                username = username_by_contact_number[_sms_message.sender]
                if username not in usernames_that_responded:
                    usernames_that_responded.append(username)

        list_items = []
        for _configuration in configurations.all():
            _participant = participants_by_username[
                _configuration.user.username]
            end_date = _configuration.closeout_date
            message_sent_date = False
            if _configuration.message:
                message_sent_date = _configuration.message.created.astimezone(
                    pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d')
            status = "Disabled"
            if _participant.enabled:
                status = "Active"
            list_items.append({
                'heartsteps_id':
                _participant.heartsteps_id,
                'status':
                status,
                'study_start':
                _participant.study_start_date.strftime('%Y-%m-%d'),
                'study_end':
                end_date.strftime('%Y-%m-%d'),
                'message_sent_date':
                message_sent_date,
                'participant_responded':
                _configuration.user.username in usernames_that_responded
            })
        context['participants'] = list_items
        return context


class MessagesReceivedView(CohortView):
    template_name = 'dashboard/messages-received.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        participants = self.query_participants()
        users = [p.user for p in participants if p.user]
        contacts = SMSContact.objects.filter(user__in=users).all()
        numbers = [c.number for c in contacts if c.number]

        messages = []
        sms_messages_list = SMSMessage.objects.filter(
            sender__in=numbers
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
                participant = DashboardParticipant.objects.get(
                    heartsteps_id=self.kwargs['participant_id'])
                self.participant = participant
            except Participant.DoesNotExist:
                raise Http404('No matching participant')
        else:
            raise Http404('No participant')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participant'] = self.participant

        adherence_messages_enabled = AdherenceMessageConfiguration.objects.filter(
            user=self.participant.user, enabled=True).count()

        context['fitbit_authorized'] = self.participant.fitbit_authorized
        context['fitbit_last_updated'] = self.participant.fitbit_last_updated

        context['configurations'] = [{
            'title':
            'Adherence Message',
            'enabled':
            adherence_messages_enabled,
            'url':
            reverse('dashboard-cohort-participant-adherence-messages',
                    kwargs={
                        'cohort_id': self.cohort.id,
                        'participant_id': self.participant.heartsteps_id
                    })
        }, {
            'title':
            'Anti-Sedentary Suggestions',
            'enabled':
            self.participant.anti_sedentary_suggestions_enabled
        }, {
            'title':
            'Walking Suggestions',
            'enabled':
            self.participant.walking_suggestions_enabled
        }, {
            'title':
            'Morning Messages',
            'enabled':
            self.participant.morning_messages_enabled
        }]

        _config = self.participant.activity_survey_configuration
        context['configurations'].append({
            'title':
            'Activity Surveys',
            'enabled':
            _config.enabled if _config else None,
            'treatment_probability':
            _config.treatment_probability if _config else None
        })

        _config = self.participant.walking_suggestion_survey_configuration
        context['configurations'].append({
            'title':
            'Walking Suggestion Surveys',
            'enabled':
            _config.enabled if _config else None,
            'treatment_probability':
            _config.treatment_probability if _config else None
        })

        burst_period_actions = []
        burst_period_actions.append({
            'name':
            'Disable' if self.participant.burst_period_enabled else 'Enable',
            'value':
            'disable' if self.participant.burst_period_enabled else 'enable',
            'url':
            reverse('dashboard-cohort-participant-burst-period-configuration',
                    kwargs={
                        'cohort_id': self.cohort.id,
                        'participant_id': self.participant.heartsteps_id
                    })
        })

        context['configurations'].append({
            'title': 'Burst Periods',
            'enabled': self.participant.burst_period_enabled,
            'actions': burst_period_actions
        })

        context['configurations'].sort(key=lambda x: x['title'])
        return context


class ParticipantBurstPeriodConfigurationView(ParticipantView):

    template_name = 'dashboard/participant-burst-period-configuration.html'

    def get_burst_configuration(self):
        try:
            return BurstPeriodConfiguration.objects \
                .prefetch_burst_periods() \
                .get(
                    user=self.participant.user
                )
        except BurstPeriodConfiguration.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def post(self, request, cohort_id, participant_id, **kwargs):
        self.setup_participant()
        config = self.get_burst_configuration()
        if 'create-daily-task' in request.POST:
            if config.daily_task:
                config.daily_task.delete()
            config.daily_task = config.create_daily_task()
            config.save()
        if 'enable' in request.POST:
            config.enabled = True
            config.save()
        if 'disable' in request.POST:
            config.enabled = False
            config.save()
        if 'create' in request.POST:
            if config:
                config.delete()
            BurstPeriodConfiguration.objects.create(user=self.participant.user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ParticipantActivitySummaryView(ParticipantView):
    template_name = 'dashboard/participant-activity-summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = [date.today() - timedelta(days=offset) for offset in range(14)]
        dates.sort()
        account = None
        try:
            au = FitbitAccountUser.objects.prefetch_related('account').get(
                user=self.participant.user)
            account = au.account
        except FitbitAccountUser.DoesNotExist:
            pass
        fitbit_activity_by_date = {}
        if account:
            fitbit_days = FitbitDay.objects.filter(account=account,
                                                   date__in=dates).all()
            for _fitbit_day in fitbit_days:
                fitbit_activity_by_date[_fitbit_day.date] = {
                    'wore_fitbit': _fitbit_day.wore_fitbit,
                    'step_count': _fitbit_day.step_count,
                    'completely_updated': _fitbit_day.completely_updated
                }
        watch_app_updates_by_date = {}
        watch_app_step_counts = WatchAppStepCount.objects.filter(
            user=self.participant.user,
            created__gte=timezone.now() -
            timedelta(days=14)).order_by('created').all()
        watch_app_step_counts = list(watch_app_step_counts)
        if account:
            fitbit_account_updates = FitbitAccountUpdate.objects.filter(
                account=account,
                created__gte=timezone.now() -
                timedelta(days=14)).order_by('created').all()
            fitbit_account_updates = list(fitbit_account_updates)
        else:
            fitbit_account_updates = []
        fitbit_account_updates_by_date = {}
        for _date in dates:
            watch_app_record_count = 0
            end_datetime = datetime(
                _date.year, _date.month, _date.day,
                tzinfo=pytz.UTC) + timedelta(days=1)
            while len(watch_app_step_counts
                      ) and watch_app_step_counts[0].created < end_datetime:
                watch_app_record_count += 1
                _step_count = watch_app_step_counts.pop(0)
            watch_app_updates_by_date[_date] = watch_app_record_count
            fitbit_update_count = 0
            while len(fitbit_account_updates
                      ) and fitbit_account_updates[0].created < end_datetime:
                fitbit_update_count += 1
                fitbit_account_updates.pop(0)
            fitbit_account_updates_by_date[_date] = fitbit_update_count
        serialized_days = []
        for _date in sorted(dates):
            _serialized = {'date': _date.strftime('%Y-%m-%d')}
            if _date in fitbit_activity_by_date:
                _serialized.update(fitbit_activity_by_date[_date])
            if _date in watch_app_updates_by_date:
                _serialized[
                    'watch_app_step_counts'] = watch_app_updates_by_date[_date]
            if _date in fitbit_account_updates_by_date:
                _serialized[
                    'fitbit_account_updates'] = fitbit_account_updates_by_date[
                        _date]
            serialized_days.append(_serialized)
        serialized_days.reverse()
        context['days'] = serialized_days
        return context


class ParticipantInterventionSummaryView(ParticipantView):
    template_name = 'dashboard/participant-intervention-summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users = []
        if self.participant.user:
            users.append(self.participant.user)

        anti_sedentary_decisions = DashboardParticipant.summaries.get_anti_sedentary_decisions(
            users=users,
            start=timezone.now() - timedelta(days=28),
            end=timezone.now())
        walking_suggestion_decisions = DashboardParticipant.summaries.get_walking_suggestions(
            users=users,
            start=timezone.now() - timedelta(days=28),
            end=timezone.now())

        time_ranges = []
        for offset in [3, 7, 14, 28]:
            time_ranges.append({
                'title':
                'Last %d days' % (offset),
                'walking_suggestion_summary':
                DashboardParticipant.summaries.summarize_walking_suggestions(
                    users=users,
                    end=timezone.now(),
                    start=timezone.now() - timedelta(days=offset),
                    decisions=walking_suggestion_decisions),
                'anti_sedentary_suggestion_summary':
                DashboardParticipant.summaries.
                summarize_anti_sedentary_suggestions(
                    users=users,
                    end=timezone.now(),
                    start=timezone.now() - timedelta(days=offset),
                    decisions=anti_sedentary_decisions),
                'watch_app_availability_summary':
                DashboardParticipant.watch_app_step_counts.summary(
                    users=users,
                    start=timezone.now() - timedelta(days=offset),
                    end=timezone.now())
            })

        context['time_ranges'] = time_ranges

        return context


class ParticipantEditView(ParticipantView):
    template_name = 'dashboard/participant-edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ParticipantEditForm(
            initial={
                'heartsteps_id': self.participant.heartsteps_id,
                'enrollment_token': self.participant.enrollment_token,
                'birth_year': self.participant.birth_year
            })
        return context

    def post(self, request, *args, **kwargs):
        form = ParticipantEditForm(request.POST, instance=self.participant)
        if form.is_valid():
            form.save()
            messages.add_message(
                request, messages.SUCCESS,
                'Updated participant %s' % (self.participant.heartsteps_id))
            return HttpResponseRedirect(
                reverse('dashboard-cohort-participant',
                        kwargs={
                            'cohort_id': self.cohort.id,
                            'participant_id': self.participant.heartsteps_id
                        }))
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return TemplateResponse(request, self.template_name, context)


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
            messages.add_message(
                request, messages.SUCCESS,
                'Created participant %s' % (participant.heartsteps_id))
            return HttpResponseRedirect(
                reverse('dashboard-cohort-participants',
                        kwargs={'cohort_id': self.cohort.id}))
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return TemplateResponse(request, self.template_name, context)


class FeatureFlagView(CohortView):
    template_name = 'dashboard/participant-feature-flags.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participants = Participant.objects \
            .filter(
                archived=False,
                cohort=self.cohort,
            ) \
            .order_by('heartsteps_id') \
            .prefetch_related('user') \
            .all()

        context['participants'] = participants

        context['study_form'] = StudyFeatureFlagEditForm(initial={
            'studywide_feature_flags':
            self.cohort.study.studywide_feature_flags
        })

        # TODO: change initial value
        context['participant_form'] = ParticipantFeatureFlagEditForm(
            initial={'flags': ""})

        context['cohort_form'] = CohortFeatureFlagEditForm(
            initial={'cohort_feature_flags': self.cohort.cohort_feature_flags})

        return context

    def post(self, request, *args, **kwargs):
        study_form = StudyFeatureFlagEditForm(request.POST,
                                              instance=self.cohort.study)

        cohort_form = CohortFeatureFlagEditForm(request.POST,
                                                instance=self.cohort)

        # TODO: add custom validation
        study_form_valid = study_form.is_valid()
        cohort_form_valid = cohort_form.is_valid()

        if study_form_valid and cohort_form_valid:
            study_form.save()
            cohort_form.save(commit=False)
            cohort_form.study = self.cohort.study
            cohort_form.save()

            messages.add_message(
                request, messages.SUCCESS,
                'Updated feature flags for study: %s' % (self.cohort.study))
            return HttpResponseRedirect(
                reverse('dashboard-cohort-participants',
                        kwargs={'cohort_id': self.cohort.id}))
        else:
            context = self.get_context_data(**kwargs)
            context['study_form'] = study_form
            context['cohort_form'] = cohort_form
            return TemplateResponse(request, self.template_name, context)


class ParticipantNotificationsView(ParticipantView):

    template_name = 'dashboard/participant-notifications.html'

    def get_notifications(self, user, start, end):
        if not user:
            return []
        notifications = PushMessage.objects.filter(
            recipient=user,
            message_type=PushMessage.NOTIFICATION,
            created__gte=start,
            created__lte=end
        ) \
            .order_by('-created') \
            .localize_datetimes() \
            .all()
        return notifications

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = self.get_notifications(
            user=self.participant.user,
            start=timezone.now() - timedelta(days=7),
            end=timezone.now())
        return context

    def post(self, request, *args, **kwargs):
        for k, v in request.POST.items():
            print("request.POST['{}']: {}".format(k, v))

        if 'message' in request.POST and request.POST['message'] is not '':
            if 'module' in request.POST and request.POST[
                    'module'] == 'generic_messages':
                generic_messages_service = GenericMessagesService.create_service(
                    username=self.participant.user.username)
                sent_message = generic_messages_service.send_message(
                    "test intervention", "Notification.GenericMessagesTest",
                    "Sample Title", "Sample Body", True)
                messages.add_message(
                    request, messages.SUCCESS,
                    'Message sent using generic_messages: /notification/{}'.
                    format(sent_message.data["messageId"]))
            else:
                try:
                    self.user = self.participant.user
                    EventLog.debug(self.user,
                                   "ParticipantNotificationsView.post():1")
                    service = PushMessageService(
                        username=self.participant.heartsteps_id)
                    EventLog.debug(
                        self.user,
                        "ParticipantNotificationsView.post():2:{}".format(
                            service))
                    EventLog.debug(
                        self.user,
                        "ParticipantNotificationsView.post():3:{}".format(
                            request.POST['message']))
                    sent_message = service.send_notification(
                        request.POST['message'])
                    EventLog.debug(
                        self.user,
                        "ParticipantNotificationsView.post():4:{}".format(
                            sent_message))
                    messages.add_message(
                        request, messages.SUCCESS,
                        'Message sent: /notification/{}'.format(
                            sent_message.data["messageId"]))
                except Exception as e:
                    EventLog.debug(
                        self.user,
                        "ParticipantNotificationsView.post():e1:{}".format(e))
                    messages.add_message(request, messages.ERROR,
                                         'Could not send message')
        else:
            messages.add_message(request, messages.ERROR, 'No message to send')
        return HttpResponseRedirect(
            reverse('dashboard-cohort-participant',
                    kwargs={
                        'participant_id': self.participant.heartsteps_id,
                        'cohort_id': self.cohort.id
                    }))


class ParticipantNotificationDetailView(ParticipantView):

    template_name = 'dashboard/participant-notification-detail.html'

    def setup_participant(self):
        super().setup_participant()
        self.setup_notification()

    def setup_notification(self):
        if 'notification_id' not in self.kwargs:
            raise Http404('No notification id')
        try:
            self.notification = PushMessage.objects.get(
                id=self.kwargs['notification_id'],
                recipient=self.participant.user
                if self.participant.user else None)
        except PushMessage.DoesNotExist:
            raise Http404('Notification does not exist')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['notification'] = self.notification
        return context

    def post(self, request, *args, **kwargs):
        self.setup_participant()
        self.notification.update_message_receipts()
        messages.add_message(request, messages.SUCCESS,
                             'Updated message receipts')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ParticipantSMSMessagesView(ParticipantView):

    template_name = 'dashboard/sms-messages.html'

    def test_func(self):
        results = super().test_func()
        if results:
            try:
                self.sms_service = SMSService(user=self.participant.user)
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

            service = SMSService(user=self.participant.user)
            service.send(body)
        context = self.get_context_data()
        context['form'] = form
        return TemplateResponse(request, self.template_name, context)


class ParticipantPageViews(ParticipantView):
    template_name = 'dashboard/participant-page-views.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.participant.user:
            page_views = PageView.objects.filter(
                user=self.participant.user,
                time__gte=timezone.now() - timedelta(days=7)
            ) \
                .order_by('-time') \
                .all()
            context['page_views'] = page_views
        return context


class ParticipantUserLogs(ParticipantView):
    template_name = 'dashboard/userlogs-list.html'

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     if self.participant.user:
    #         page_views = PageView.objects.filter(
    #             user = self.participant.user,
    #             time__gte = timezone.now() - timedelta(days=7)
    #         ) \
    #         .order_by('-time') \
    #         .all()
    #         context['page_views'] = page_views
    #     return context


class ParticipantFeatureToggleView(ParticipantView):
    template_name = 'dashboard/participant-feature-toggle.html'

    def redirect(self, request):
        return HttpResponseRedirect(
            reverse('dashboard-cohort-participant',
                    kwargs={
                        'participant_id': self.participant.heartsteps_id,
                        'cohort_id': self.cohort.id
                    }))

    def add_success_message(self, request, message):
        messages.add_message(request, messages.SUCCESS, message)

    def add_error_message(self, request, message):
        messages.add_message(request, messages.ERROR, message)

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
                user=self.participant.user)
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
                user=self.participant.user)
            config.enabled = False
            config.save()
            self.add_success_message(request, 'Disabled adherence messages')
        else:
            config, _ = AdherenceMessageConfiguration.objects.get_or_create(
                user=self.participant.user)
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
        service = ParticipantService(participant=self.participant)
        service.disable()
        self.add_success_message(
            request, 'Disabled %s' % (self.participant.user.username))
        return self.redirect(request)


class ParticipantEnableView(ParticipantFeatureToggleView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Enable %s' % (self.participant.heartsteps_id)
        context['action'] = 'Enable Participant'
        return context

    def post(self, request, *args, **kwargs):
        service = ParticipantService(participant=self.participant)
        service.enable()
        self.add_success_message(
            request, 'Enabled %s' % (self.participant.user.username))
        return self.redirect(request)


class ParticipantAdherenceView(ParticipantView):

    template_name = 'dashboard/participant-adherence.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        adherence_summaries = self.participant.get_adherence_during(
            start=date.today() - timedelta(days=14), end=date.today())
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


class ParticipantSendTestWalkingSuggestionSurvey(ParticipantView):
    def post(self, request, *args, **kwargs):
        if self.participant.user:
            try:
                configuration = WalkingSuggestionSurveyConfiguration.objects.get(
                    user=self.participant.user)
                survey = configuration.create_survey()
                try:
                    survey.send_notification()
                    messages.add_message(request, messages.SUCCESS,
                                         'Survey sent')
                except survey.NotificationSendError:
                    messages.add_message(request, messages.ERROR,
                                         'Could not send survey')
            except WalkingSuggestionSurveyConfiguration.DoesNotExist:
                messages.add_message(
                    request, messages.ERROR,
                    'Walking suggestion configuration does not exist')
        else:
            messages.add_message(request, messages.ERROR, 'Not enabled')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CohortAddStudyTypeView(CohortView):

    template_name = 'dashboard/cohort-add-studytype.html'

    def post(self, request, *args, **kwargs):
        if self.cohort.id:
            study_type_service = StudyTypeService("NLM", user=request.user)
            study_type_service.assign_cohort(self.cohort)
            messages.add_message(
                request, messages.SUCCESS,
                'cohort is flagged as "NLM" cohort: cohort_id={}, cohort_name={}'
                .format(self.cohort.id, self.cohort.name))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CohortWalkingSuggestionSurveyView(CohortView):

    template_name = 'dashboard/cohort-walking-suggestion-surveys.html'

    def get_context_data(self, start=None, end=None, **kwargs):
        context = super().get_context_data(**kwargs)

        if start and end:
            try:
                start_datetime = datetime.strptime(start, '%Y-%m-%d')
                end_datetime = datetime.strptime(end, '%Y-%m-%d')
            except ValueError:
                raise Http404('Not a date')
        else:
            start_datetime = datetime.now() - timedelta(days=7)
            end_datetime = datetime.now()

        time_difference = end_datetime - start_datetime
        dates = [
            end_datetime.date() - timedelta(days=offset)
            for offset in range(time_difference.days + 1)
        ]
        dates.sort()
        start_datetime = datetime(dates[0].year,
                                  dates[0].month,
                                  dates[0].day,
                                  tzinfo=pytz.timezone('America/Los_Angeles'))
        end_datetime = start_datetime + timedelta(days=len(dates))

        participants = self.query_participants().filter(archived=False,
                                                        active=True).all()
        users = [p.user for p in participants if p.user]

        summary_by_date = {}
        for date in dates:
            summary_by_date[date] = {
                'decisions': 0,
                'decisions_to_treat': 0,
                'surveys': 0,
                'surveys_answered': 0,
                'messages_sent': 0,
                'messages_opened': 0
            }
        decisions_by_user_id_by_date = {}
        decisions = WalkingSuggestionSurveyDecision.objects.filter(
            user__in=users,
            created__gte=start_datetime,
            created__lte=end_datetime).all()
        for decision in decisions:
            decision_date = decision.created.astimezone(
                pytz.timezone('America/Los_Angeles')).date()
            summary_by_date[decision_date]['decisions'] += 1
            if decision.treated:
                summary_by_date[decision_date]['decisions_to_treat'] += 1
            if decision.user_id not in decisions_by_user_id_by_date:
                decisions_by_user_id_by_date[decision.user_id] = {}
            if decision_date not in decisions_by_user_id_by_date[
                    decision.user_id]:
                decisions_by_user_id_by_date[
                    decision.user_id][decision_date] = []
            decisions_by_user_id_by_date[
                decision.user_id][decision_date].append(decision)

        walking_suggestion_surveys = WalkingSuggestionSurvey.objects.filter(
            user__in=users,
            created__gte=start_datetime,
            created__lte=end_datetime).all()
        walking_suggestion_surveys_by_user_id = {}
        for survey in walking_suggestion_surveys:
            survey_date = survey.created.astimezone(
                pytz.timezone('America/Los_Angeles')).date()
            summary_by_date[survey_date]['surveys'] += 1
            if survey.answered:
                summary_by_date[survey_date]['surveys_answered'] += 1
            if survey.user_id not in walking_suggestion_surveys_by_user_id:
                walking_suggestion_surveys_by_user_id[survey.user_id] = []
            survey._date = survey_date
            walking_suggestion_surveys_by_user_id[survey.user_id].append(
                survey)

        messages_by_user_id_by_date = {}
        messages = PushMessage.objects.filter(
            recipient__in=users,
            collapse_subject='walking_suggestion_survey',
            created__gte=start_datetime,
            created__lte=end_datetime)
        for message in messages:
            message_date = message.created.astimezone(
                pytz.timezone('America/Los_Angeles')).date()
            user_id = message.recipient_id
            if user_id not in messages_by_user_id_by_date:
                messages_by_user_id_by_date[user_id] = {}
            if message_date not in messages_by_user_id_by_date[user_id]:
                messages_by_user_id_by_date[user_id][message_date] = []
            messages_by_user_id_by_date[user_id][message_date].append(message)
            if message.sent:
                summary_by_date[message_date]['messages_sent'] += 1
            if message.opened:
                summary_by_date[message_date]['messages_opened'] += 1

        configurations_by_user_id = {}
        configurations = WalkingSuggestionSurveyConfiguration.objects.filter(
            user__in=users).all()
        for configuration in configurations:
            configurations_by_user_id[configuration.user_id] = configuration

        serialized_participants = []
        for participant in participants:
            serialized_dates = []
            for _date in dates:
                serialized_decisions = []
                if participant.user and participant.user.id in decisions_by_user_id_by_date and _date in decisions_by_user_id_by_date[
                        participant.user.id]:
                    for _decision in decisions_by_user_id_by_date[
                            participant.user.id][_date]:
                        serialized_decisions.append({
                            'time':
                            _decision.created.astimezone(
                                pytz.timezone('America/Los_Angeles')).strftime(
                                    '%H:%M:%S'),
                            'treatment_probability':
                            _decision.treatment_probability,
                            'treated':
                            _decision.treated
                        })
                serialized_surveys = []
                if participant.user and participant.user.id in walking_suggestion_surveys_by_user_id:
                    for survey in walking_suggestion_surveys_by_user_id[
                            participant.user.id]:
                        if survey._date.strftime('%Y-%m-%d') != _date.strftime(
                                '%Y-%m-%d'):
                            continue
                        serialized_surveys.append({
                            'id':
                            survey.id,
                            'time':
                            survey.created.astimezone(
                                pytz.timezone('America/Los_Angeles')).strftime(
                                    '%H:%M:%S'),
                            'answered':
                            survey.answered
                        })
                serialized_messages = []
                if participant.user and participant.user.id in messages_by_user_id_by_date and _date in messages_by_user_id_by_date[
                        participant.user.id]:
                    for message in messages_by_user_id_by_date[
                            participant.user.id][_date]:
                        serialized_messages.append({
                            'id':
                            str(message.uuid),
                            'sent':
                            message.sent.astimezone(
                                pytz.timezone('America/Los_Angeles')).strftime(
                                    '%H:%M:%S') if message.sent else None
                        })
                serialized_dates.append({
                    'decisions': serialized_decisions,
                    'surveys': serialized_surveys,
                    'messages': serialized_messages
                })
            configured = 'No Configuration'
            if participant.user and participant.user.id in configurations_by_user_id:
                configuration = configurations_by_user_id[participant.user.id]
                if not configuration.enabled:
                    configured = 'Not Enabled'
                elif configuration.treatment_probability is None:
                    configured = 'No Treatment Probability'
                else:
                    configured = 'Treatment Probability: {probability:.0%}'.format(
                        probability=configuration.treatment_probability)
            serialized_participants.append({
                'heartsteps_id': participant.heartsteps_id,
                'dates': serialized_dates,
                'configured': configured
            })
        context['participants'] = serialized_participants
        context['dates'] = [_date.strftime('%Y-%m-%d') for _date in dates]
        context['decisions_by_date'] = [
            summary_by_date[_date]['decisions'] for _date in dates
        ]
        context['decisions_to_treat_by_date'] = [
            summary_by_date[_date]['decisions_to_treat'] for _date in dates
        ]
        context['surveys_by_date'] = [
            summary_by_date[_date]['surveys'] for _date in dates
        ]
        context['surveys_answered_by_date'] = [
            summary_by_date[_date]['surveys_answered'] for _date in dates
        ]
        context['messages_sent_by_date'] = [
            summary_by_date[_date]['messages_sent'] for _date in dates
        ]
        context['messages_opened_by_date'] = [
            summary_by_date[_date]['messages_opened'] for _date in dates
        ]
        return context


class CohortMorningMessagesView(CohortView):

    template_name = 'dashboard/cohort-morning-messages.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        last_week = [
            date.today() - timedelta(days=offset) for offset in range(7)
        ]

        participants = self.query_participants().filter(archived=False,
                                                        active=True).all()
        users = [p.user for p in participants if p.user]

        morning_messages = MorningMessage.objects.filter(user__in=users, date__in=last_week) \
            .prefetch_message() \
            .prefetch_survey() \
            .all()

        morning_messages_by_user_id_by_date = {}
        counts_by_date = {}
        for _date in last_week:
            counts_by_date[_date] = {
                'sent': 0,
                'opened': 0,
                'answered': 0,
                'answered_fully': 0
            }
        for morning_message in morning_messages:
            _date = morning_message.date
            _user_id = morning_message.user_id
            if _user_id not in morning_messages_by_user_id_by_date:
                morning_messages_by_user_id_by_date[_user_id] = {}
            morning_messages_by_user_id_by_date[_user_id][
                _date] = morning_message
            if morning_message.message and morning_message.message.sent:
                counts_by_date[_date]['sent'] += 1
            if morning_message.message and morning_message.message.opened:
                counts_by_date[_date]['opened'] += 1
            if morning_message.message and morning_message.survey.answered:
                counts_by_date[_date]['answered'] += 1
            if hasattr(morning_message.survey, '_answers') and hasattr(
                    morning_message.survey, '_questions'):
                if len(morning_message.survey._answers) == len(
                        morning_message.survey._questions):
                    counts_by_date[_date]['answered_fully'] += 1

        configurations = MorningMessageConfiguration.objects \
            .filter(user__in=users) \
            .prefetch_related(Prefetch('daily_task', queryset=DailyTask.objects.prefetch_related('task'))) \
            .all()
        configuration_by_user_id = {}
        for configuration in configurations:
            configuration_by_user_id[configuration.user_id] = configuration

        context['dates'] = [_date.strftime('%Y-%m-%d') for _date in last_week]
        context['sent_by_date'] = [
            counts_by_date[_date]['sent'] for _date in last_week
        ]
        context['opened_by_date'] = [
            counts_by_date[_date]['opened'] for _date in last_week
        ]
        context['answered_by_date'] = [
            counts_by_date[_date]['answered'] for _date in last_week
        ]
        context['answered_fully_by_date'] = [
            counts_by_date[_date]['answered_fully'] for _date in last_week
        ]

        serialized_participants = []
        for participant in participants:
            serialized_participant = {
                'heartsteps_id': participant.heartsteps_id,
                'morning_messages': [{} for _date in last_week],
                'last_morning_message': None,
                'enabled': False,
                'daily_task': False
            }
            if participant.user and participant.user.id in configuration_by_user_id:
                configuraiton = configuration_by_user_id[participant.user.id]
                if configuraiton.enabled:
                    serialized_participant['enabled'] = True
                if configuraiton.daily_task:
                    pass
                    if configuraiton.daily_task.task.last_run_at:
                        serialized_participant[
                            'daily_task'] = "Last run at %s" % (
                                configuraiton.daily_task.task.last_run_at.
                                strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        serialized_participant['daily_task'] = "Never run"
            if participant.user and participant.user.id in morning_messages_by_user_id_by_date:
                serialized_morning_messages = []
                for _date in last_week:
                    if _date in morning_messages_by_user_id_by_date[
                            participant.user.id]:
                        morning_message = morning_messages_by_user_id_by_date[
                            participant.user.id][_date]
                        survey_answered_fully = None
                        number_of_questions = 0
                        number_of_answers = 0
                        if morning_message.survey:
                            number_of_answers = len(
                                getattr(morning_message.survey, '_answers',
                                        []))
                            number_of_questions = len(
                                getattr(morning_message.survey, '_questions',
                                        []))
                            if morning_message.survey.answered and number_of_answers == number_of_questions:
                                survey_answered_fully = True
                        serialized_morning_messages.append({
                            'id':
                            morning_message.id
                            if morning_message.survey else None,
                            'sent':
                            morning_message.message.sent.strftime(
                                '%Y-%m-%d %H:%M:%S') if morning_message.message
                            and morning_message.message.sent else None,
                            'opened':
                            morning_message.message.opened.strftime(
                                '%Y-%m-%d %H:%M:%S') if morning_message.message
                            and morning_message.message.opened else None,
                            'survey_answered':
                            morning_message.survey.answered
                            if morning_message.survey else None,
                            'survey_answered_fully':
                            survey_answered_fully,
                            'number_of_questions':
                            number_of_questions,
                            'number_of_answers':
                            number_of_answers
                        })
                    else:
                        serialized_morning_messages.append({})
                serialized_participant[
                    'morning_messages'] = serialized_morning_messages
            serialized_participants.append(serialized_participant)
        context['participants'] = serialized_participants
        return context


class ParticipantMorningMessagesView(ParticipantView):

    template_name = 'dashboard/participant-morning-messages.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.participant.user:
            try:
                context['configuration'] = MorningMessageConfiguration.objects \
                    .prefetch_related('daily_task') \
                    .get(user=self.participant.user)
            except MorningMessageConfiguration.DoesNotExist:
                pass

        if self.participant.user:
            morning_messages = MorningMessage.objects \
                .filter(
                    user=self.participant.user
                ) \
                .order_by('-date') \
                .prefetch_decision() \
                .prefetch_message() \
                .prefetch_survey() \
                .prefetch_timezone() \
                .all()
        else:
            morning_messages = []

        serialized_morning_messages = []
        for _morning_message in morning_messages:
            completed = 'Not Completed'
            opened = 'Not Opened'
            received = 'Not Received'
            sent = 'Not Sent'
            if _morning_message.message:
                _timezone = _morning_message.timezone
                if _morning_message.message.engaged:
                    completed = _morning_message.message.engaged.astimezone(
                        _timezone).strftime('%Y-%m-%d %H:%M:%S')
                if _morning_message.message.opened:
                    opened = _morning_message.message.opened.astimezone(
                        _timezone).strftime('%Y-%m-%d %H:%M:%S')
                if _morning_message.message.received:
                    received = _morning_message.message.received.astimezone(
                        _timezone).strftime('%Y-%m-%d %H:%M:%S')
                if _morning_message.message.sent:
                    sent = _morning_message.message.sent.astimezone(
                        _timezone).strftime('%Y-%m-%d %H:%M:%S')
            message_frames = []
            if _morning_message.is_loss_framed:
                message_frames.append('Loss')
            if _morning_message.is_gain_framed:
                message_frames.append('Gain')
            if _morning_message.is_sedentary_framed:
                message_frames.append('Sedentary')
            if _morning_message.is_active_framed:
                message_frames.append('Active')
            if message_frames:
                message_frame = ','.join(sorted(message_frames))
            else:
                message_frame = 'Not framed'
            survey_status = 'Missing'
            questions = []
            if _morning_message.survey:
                if _morning_message.survey.answered:
                    survey_status = 'Answered'
                else:
                    survey_status = 'Unanswered'
                if _morning_message.survey._questions:
                    for _question in _morning_message.survey._questions:
                        answer_value = None
                        if hasattr(
                                _morning_message.survey, '_answers'
                        ) and _question.id in _morning_message.survey._answers:
                            answer = _morning_message.survey._answers[
                                _question.id]
                            answer_value = answer.label
                        questions.append({
                            'answer': answer_value,
                            'label': _question.label,
                            'name': _question.name
                        })
            serialized_morning_messages.append({
                'date':
                _morning_message.date.strftime('%Y-%m-%d'),
                'notification':
                _morning_message.notification,
                'anchor':
                _morning_message.anchor,
                'completed':
                completed,
                'sent':
                sent,
                'opened':
                opened,
                'received':
                received,
                'message_frame':
                message_frame,
                'survey_status':
                survey_status,
                'questions':
                questions
            })

        context['morning_messages'] = serialized_morning_messages
        return context

    def post(self, request, *args, **kwargs):
        if self.participant.user:
            try:
                configuration = MorningMessageConfiguration.objects.get(
                    user=self.participant.user)
                if not configuration.daily_task:
                    configuration.create_daily_task()
                if configuration.enabled:
                    messages.add_message(request, messages.SUCCESS,
                                         'Morning messages disabled')
                    configuration.enabled = False
                else:
                    messages.add_message(request, messages.SUCCESS,
                                         'Morning messages enabled')
                    configuration.enabled = True
                configuration.save()
            except MorningMessageConfiguration.DoesNotExist:
                MorningMessageConfiguration.objects.create(
                    user=self.participant.user)
                messages.add_message(request, messages.SUCCESS,
                                     'Morning message configuration created')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Participant disabled')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class ParticipantExportView(ParticipantView):

    template_name = 'dashboard/participant-export.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        exports = DataExport.objects.filter(
            user=self.participant.user).order_by('-start')[:100]
        serialized_exports = []
        for _export in exports:
            serialized_exports.append({
                'error':
                _export.error_message,
                'filename':
                _export.filename,
                'time':
                _export.start.strftime('%Y-%m-%d %H:%M:%S'),
                'duration':
                '%d seconds' % (_export.duration)
            })
        context['export_logs'] = serialized_exports
        return context


class ParticipantBurstPeriodView(ParticipantView):

    template_name = 'dashboard/participant-burst-period.html'

    def get_burst_period(self, burst_period_id):
        if burst_period_id is None:
            return BurstPeriod()
        try:
            return BurstPeriod.objects.get(id=burst_period_id,
                                           user=self.participant.user)
        except BurstPeriod.DoesNotExist:
            raise Http404('Not found')

    def get_context_data(self, burst_period_id=None, **kwargs):
        context = super().get_context_data(**kwargs)
        burst_period = self.get_burst_period(burst_period_id)
        context['burst_period'] = burst_period
        context['form'] = BurstPeriodForm(initial={
            'start': burst_period.start,
            'end': burst_period.end
        })
        return context

    def post(self, request, burst_period_id=None, **kwargs):
        burst_period = self.get_burst_period(burst_period_id)
        form = BurstPeriodForm(request.POST)
        if form.is_valid():
            burst_period.user = self.participant.user
            burst_period.start = form.cleaned_data['start']
            burst_period.end = form.cleaned_data['end']
            burst_period.save()
            try:
                configuration = BurstPeriodConfiguration.objects.get(
                    user=burst_period.user)
                configuration.set_current_intervention_configuration()
            except BurstPeriodConfiguration.DoesNotExist:
                pass
            messages.add_message(request, messages.SUCCESS,
                                 'Created burst period')
            return HttpResponseRedirect(
                reverse('dashboard-cohort-participant',
                        kwargs={
                            'cohort_id': self.cohort.id,
                            'participant_id': self.participant.heartsteps_id
                        }))
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return TemplateResponse(request, self.template_name, context)


class ParticipantBurstPeriodDeleteView(ParticipantBurstPeriodView):
    def post(self, request, burst_period_id, **kwargs):
        burst_period = self.get_burst_period(burst_period_id)
        burst_period.delete()
        try:
            configuration = BurstPeriodConfiguration.objects.get(
                user=burst_period.user)
            configuration.set_current_intervention_configuration()
        except BurstPeriodConfiguration.DoesNotExist:
            pass
        messages.add_message(request, messages.SUCCESS, 'Deleted burst period')
        return HttpResponseRedirect(
            reverse('dashboard-cohort-participant',
                    kwargs={
                        'cohort_id': self.cohort.id,
                        'participant_id': self.participant.heartsteps_id
                    }))


class ClockFaceList(TemplateView):

    template_name = 'dashboard/clock-face-list.html'

    def test_func(self):
        if self.request.user and not self.request.user.is_anonymous:
            admin_for_studies = Study.objects.filter(admins=self.request.user)
            self.admin_for_studies = list(admin_for_studies)
            if self.request.user.is_staff or self.admin_for_studies:
                return True
        return False

    def get_context_data(self):
        clock_faces = ClockFace.objects \
            .exclude(
                user=None
            ) \
            .prefetch_related('user') \
            .all()
        users = [
            clock_face.user for clock_face in clock_faces if clock_face.user
        ]

        logs_by_username = {}
        clock_face_logs = ClockFaceLog.objects \
            .filter(
                user__in=users,
                time__gte=timezone.now() - timedelta(days=7)
            ) \
            .prefetch_related('user') \
            .all()
        for log in clock_face_logs:
            if log.user.username not in logs_by_username:
                logs_by_username[log.user.username] = []
            logs_by_username[log.user.username].append(log)

        step_counts_by_username = {}
        step_counts = StepCount.objects.filter(
            user__in=users, start__gte=timezone.now() -
            timedelta(days=7)).prefetch_related('user')
        for count in step_counts:
            if count.user.username not in step_counts_by_username:
                step_counts_by_username[count.user.username] = []
            step_counts_by_username[count.user.username].append(count)

        for clock_face in clock_faces:
            if not clock_face.user:
                continue
            if clock_face.user.username in logs_by_username:
                logs = logs_by_username[clock_face.user.username]
                clock_face.log_count = len(logs)
                clock_face.last_log = logs[-1]
            if clock_face.user.username in step_counts_by_username:
                counts = step_counts_by_username[clock_face.user.username]
                clock_face.step_count_count = len(counts)
                clock_face.last_step_count = counts[-1]
        return {'clock_faces': clock_faces}


class UserLogsList(TemplateView):
    template_name = 'dashboard/userlogs-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_staff"] = self.request.user.is_staff
        context["users"] = list(User.objects.order_by("username").all())

        return context

    def post(self, request, *args, **kwargs):
        default_pagesize = 20

        context = self.get_context_data(**kwargs)

        context["is_staff"] = self.request.user.is_staff
        context["users"] = list(User.objects.order_by("username").all())

        selected_user = self.request.POST["selected_user"]
        context["selected_user"] = selected_user
        selected_user_obj = User.objects.get(username=selected_user)

        # use this thing if you need to generate debugging logs
        # for i in range(100):
        #     EventLog.log(User.objects.get(username=selected_user), "test {}".format(i), EventLog.DEBUG)

        # use this thing if you need system log testing
        # EventLog.log(None, "system log test", EventLog.DEBUG)

        def in_range(value, min, max):
            if value > max:
                return max
            elif value < min:
                return min
            else:
                return value

        # default page size is default_pagesize
        try:
            pagesize = in_range(
                int(request.POST.get('pagesize', default_pagesize)), 10, 100)
        except:
            pagesize = default_pagesize

        # default page number is 1
        try:
            page = int(request.POST.get('page', 1))
        except:
            page = 1

        user_logs = EventLog.objects.filter(
            user=selected_user_obj
        ).order_by('-timestamp') \
            .all()

        paginator = Paginator(user_logs, pagesize)

        page = in_range(page, 1, paginator.num_pages)

        page_obj = paginator.get_page(page)

        # if you don't have any log, you might want to see empty logs with 200, not 404. 404 usually means you're knocking on non-existing door.
        serialized_user_logs = []
        server_time = datetime.now()

        for user_log in page_obj:
            serialized_user_logs.append({
                # 'timestamp': user_log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'timestamp': user_log.timestamp,
                'status': user_log.status,
                'action': user_log.action
            })

        context['logs'] = serialized_user_logs
        context['page'] = page
        context['pagesize'] = pagesize
        context['num_pages'] = paginator.num_pages
        context['pages'] = range(1, paginator.num_pages + 1)
        context['server_time'] = str(server_time)

        return TemplateResponse(request, self.template_name, context)


class ParticipantClockFaceView(ParticipantView):

    template_name = 'dashboard/participant-clock-face.html'

    def get_clock_face(self):
        if not self.participant.user:
            return None
        try:
            return ClockFace.objects.get(user=self.participant.user)
        except ClockFace.DoesNotExist:
            return None

    def get_recent_clock_face_logs(self):
        if not self.participant.user:
            return []
        clock_face_logs = ClockFaceLog.objects.filter(
            user=self.participant.user,
            time__gte=timezone.now() - timedelta(days=7)).all()
        return list(clock_face_logs)

    def get_recent_step_counts(self):
        if not self.participant.user:
            return []
        step_counts = StepCount.objects.filter(user=self.participant.user,
                                               start__gte=timezone.now() -
                                               timedelta(days=7)).all()
        return list(step_counts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pair_form'] = ClockFacePairForm()
        context['clock_face'] = self.get_clock_face()

        clock_face_logs = self.get_recent_clock_face_logs()
        if clock_face_logs:
            context['last_log'] = clock_face_logs[-1]
            context['log_count'] = len(clock_face_logs)

        step_counts = self.get_recent_step_counts()
        if step_counts:
            context['last_step_count'] = step_counts[-1]
            context['step_count_count'] = len(step_counts)
        return context

    def post(self, request, **kwargs):
        clock_face = self.get_clock_face()
        if clock_face:
            clock_face.delete()
            messages.add_message(request, messages.SUCCESS,
                                 'Unpaired clock face')
        else:
            pair_form = ClockFacePairForm(request.POST)
            if pair_form.is_valid():
                pin = pair_form.cleaned_data['pin']
                try:
                    clock_face = ClockFace.objects.get(pin=pin, user=None)
                    clock_face.user = self.participant.user
                    clock_face.save()
                    messages.add_message(request, messages.SUCCESS,
                                         'Paired participant')
                except ClockFace.DoesNotExist:
                    messages.add_message(
                        request, messages.ERROR,
                        'Pin does not exist, or is deactivated')
            else:
                messages.add_message(request, messages.ERROR, 'Invalid form')
        return HttpResponseRedirect(
            reverse('dashboard-cohort-participant-clock-face',
                    kwargs={
                        'cohort_id': self.cohort.id,
                        'participant_id': self.participant.heartsteps_id
                    }))


def fill_context(request, context):
    if request.method == 'POST':
        request_dict = request.POST
    elif request.method == 'GET':
        request_dict = request.GET
    else:
        raise NotImplementedError('{} method is not supported'.format(
            request.method))

    pprint.pprint("fill_context():")
    pprint.pprint(">> request:")
    pprint.pprint(">>>> {}".format(request))
    pprint.pprint(">> request_dict:")
    pprint.pprint(">>>> {}".format(request_dict))
    pprint.pprint(">> context (before):")
    pprint.pprint(">>>> {}".format(context))

    if hasattr(request, 'user'):
        context["user"] = request.user
        context["is_staff"] = request.user.is_staff
        context["is_superuser"] = request.user.is_superuser

        if context["is_staff"]:
            context["my_studies"] = list(
                Study.objects.filter(admins=request.user))

    context["users"] = list(User.objects.order_by("username").all())
    context['server_time'] = str(datetime.now())

    selected_user_obj = None
    if 'selected_user' in request_dict:
        selected_username = request_dict["selected_user"]
        if isinstance(selected_username, list) and len(selected_username) == 1:
            selected_username = selected_username[0]
        if selected_username != '':
            context["selected_user"] = selected_username
            selected_user_obj = User.objects.get(username=selected_username)

    if 'selected_date' in request_dict:
        selected_date = request_dict['selected_date']
    elif selected_user_obj:
        day_service = DayService(user=selected_user_obj)
        selected_date = day_service.get_current_date()
        context["day_service"] = day_service
    else:
        selected_date = datetime.today()
    context["selected_date"] = selected_date

    if 'item' in request_dict:
        item_list = request_dict['item']
        if len(item_list) == 1:
            context["item"] = item_list[0]
        else:
            context["item"] = item_list

    if 'start_time' in request_dict:
        start_time = request_dict['start_time']
        if 'end_time' in request_dict:
            end_time = request_dict['end_time']
        else:
            end_time = start_time + timedelta(days=1)
    else:
        if "day_service" in context:
            day_service = context["day_service"]
            start_time = day_service.get_start_of_day(selected_date)
        else:
            start_time = datetime(selected_date.year, selected_date.month,
                                  selected_date.day)
        end_time = start_time + timedelta(days=1)

    context["start_time"] = start_time
    context["end_time"] = end_time

    print(">> context (after):")
    print(">>>> {}".format(context))


class ChartView(TemplateView):
    template_name = 'dashboard/chart-view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fill_context(self.request, context)

        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        fill_context(self.request, context)

        return TemplateResponse(request, self.template_name, context)


class ChartDataView:
    def dashboard_chart_data_json(request):
        context = {}

        fill_context(request, context)

        if "item" in context:
            if context["item"] == 'steps':
                from fitbit_activities.models import FitbitMinuteStepCount
                from fitbit_api.models import FitbitAccount

                fitbit_account_user = FitbitAccountUser.objects.filter(
                    user__username=context["selected_user"]).first()

                if fitbit_account_user:
                    fitbit_account = fitbit_account_user.account

                    data = [{
                        "x": obj["time"],
                        "y": obj["steps"]
                    }
                            for obj in FitbitMinuteStepCount.objects.filter(
                                account=fitbit_account,
                                time__gte=context["start_time"],
                                time__lt=context["end_time"]).values(
                                    'time', 'steps').all()]
                else:
                    print("No connected Fitbit Account")
                    data = []
            elif context["item"] == 'logs':
                data = [{
                    "id": 1,
                    "content": "item 1",
                    "start": "2014-04-20 14:00"
                }, {
                    "id": 2,
                    "content": "item 2",
                    "start": "2014-04-20 07:31"
                }, {
                    "id": 3,
                    "content": "item 3",
                    "start": "2014-04-20 11:22"
                }, {
                    "id": 4,
                    "content": "item 4",
                    "start": "2014-04-20 10:00",
                    "end": "2014-04-20 10:30"
                }, {
                    "id": 5,
                    "content": "item 5",
                    "start": "2014-04-20 15:00"
                }, {
                    "id": 6,
                    "content": "item 6",
                    "start": "2014-04-20 17:00",
                    "type": "point"
                }]
            else:
                raise NotImplementedError('{} is not supported'.format(
                    context["item"]))
            return JsonResponse(data, safe=False)
        else:
            raise NotImplementedError('"item" is not found')
