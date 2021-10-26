from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils import timezone
from django.utils.dateformat import format

from rest_framework.authtoken.models import Token
from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule

from fitbit_activities.tasks import update_all_fitbit_data
from fitbit_api.services import FitbitService

from .models import Cohort
from .models import Participant
from .models import Study
from .models import NightlyUpdateRecord
from .services import ParticipantService
from .tasks import export_user_data

def queue_export_participant_data(modeladmin, request, queryset):
    successes = 0
    fails = 0
    for p in queryset.all():
        if p.user:
            export_user_data.apply_async(
                kwargs = {
                    'username': p.user.username
                }
            )
            successes += 1
        else:
            fails += 1
    if successes > 0:
        messages.add_message(request, messages.SUCCESS, 'Export for %d participants is queued' % (successes))
    if fails > 0:
        messages.add_message(request.messages.ERROR, 'Failed to export %d paricipants' % (fails))

def initialize_participant(modeladmin, request, queryset):
    for participant in queryset.all():
        service = ParticipantService(participant)
        service.initialize()
        messages.add_message(request, messages.SUCCESS, '%s initialized' % (participant.heartsteps_id))

def deactivate_participant(modeladmin, request, queryset):
    for participant in queryset.all():
        service = ParticipantService(participant)
        service.deactivate()
        messages.add_message(request, messages.SUCCESS, '%s deactivated' % (participant.heartsteps_id))

def update_participant(modeladmin, request, queryset):
    for participant in queryset.all():
        service = ParticipantService(participant)
        service.update()
        messages.add_message(request, messages.SUCCESS, 'Ran update for %s' % (participant.heartsteps_id))

def reload_fitbit_data(modeladmin, request, queryset):
    for participant in queryset.all():
        try:
            account = FitbitService.get_account(user=participant.user)
            update_all_fitbit_data.apply_async(kwargs={
                'fitbit_user': account.fitbit_user
            })
            messages.add_message(request, messages.SUCCESS, 'Update fitbit account %s for %s' % (account.fitbit_user, participant.heartsteps_id))
        except FitbitService.NoAccount:
            messages.add_message(request, messages.ERROR, '%s has no fitbit account' % (participant.heartsteps_id))

def make_add_to_cohort(cohort):
    def add_participants_to_cohort(modeladmin, request, queryset):
        queryset.update(
            cohort = cohort
        )
        messages.add_message(
            request,
            messages.SUCCESS,
            'Added %s to %s' % (
                ', '.join([participant.heartsteps_id for participant in queryset]),
                cohort.name
            )
        )
    add_participants_to_cohort.short_description = 'Add to "%s" cohort' % cohort.name
    add_participants_to_cohort.__name__ = 'add_participants_to_cohort_%s' % cohort.id
    return add_participants_to_cohort

class ParticipantCohortFilter(admin.SimpleListFilter):
    title = 'Participant Cohort Filters'
    parameter_name = 'cohort'

    def lookups(self, request, model_admin):
        lookups = []
        for cohort in Cohort.objects.all():
            lookups.append((cohort.id, cohort.name))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            users = []
            query = Participant.objects.filter(
                cohort__id = self.value()
            )
            for participant in query.all():
                if participant.user:
                    users.append(participant.user)
            return queryset.filter(user__in=users)
        else:
            return queryset

class ParticipantAdmin(admin.ModelAdmin):
    readonly_fields = ['daily_update']

    list_display = ['__str__', 'enrolled', 'active']
    list_filter = [ParticipantCohortFilter]

    actions = [
        initialize_participant,
        deactivate_participant,
        update_participant,
        reload_fitbit_data,
        queue_export_participant_data
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)

        for cohort in Cohort.objects.all():
            action = make_add_to_cohort(cohort)
            actions[action.__name__] = (
                action,
                action.__name__,
                action.short_description
            )
        return actions

    def daily_update(self, instance):
        if instance.daily_task:
            next_run_datetime = instance.daily_task.get_next_run_time()
            if next_run_datetime:
                return 'Next update at %s' % (format(next_run_datetime, settings.DATETIME_FORMAT))
            else:
                return 'No next run?'
        else:
            return 'No daily update'
    
    daily_update.short_description = 'Daily update'

admin.site.register(Participant, ParticipantAdmin)

class ParticipantInlineAdmin(admin.TabularInline):
    model = Participant
    extra = 0

class CohortAdmin(admin.ModelAdmin):

    list_display = ['name', 'study']

    inlines = [
        ParticipantInlineAdmin
    ]

admin.site.register(Cohort, CohortAdmin)

class StudyAdmin(admin.ModelAdmin):
    pass
admin.site.register(Study, StudyAdmin)


class NightlyUpdateRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'start', 'end', 'error']
    
    readonly_fields = ['user', 'date', 'start', 'end', 'error']


admin.site.register(NightlyUpdateRecord, NightlyUpdateRecordAdmin)