import random

from django.contrib import admin
from django.contrib import messages

from import_export import resources
from import_export.fields import Field
from import_export.admin import ExportMixin

from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin
from randomization.resources import DecisionResource
from service_requests.admin import ServiceRequestAdmin

from walking_suggestion_times.models import SuggestionTime

from walking_suggestions.models import SuggestionTime, Configuration
from walking_suggestions.models import WalkingSuggestionDecision
from walking_suggestions.models import WalkingSuggestionMessageTemplate
from walking_suggestions.models import WalkingSuggestionServiceRequest
from walking_suggestions.services import WalkingSuggestionDecisionService
from walking_suggestions.services import WalkingSuggestionService

class WalkingSuggestionDecisionResource(DecisionResource):

    class Meta:
        model = WalkingSuggestionDecision
        fields = [
            'id',
            'user__username',
            'local_time',
            'test',
            'imputed',
            'available',
            'unavailable_reason',
            'treated',
            'treatment_probability',
            'sent_time',
            'received_time',
            'opened_time',
            'engaged_time',
            'message',
            'all_tags'
        ]
        export_order = [
            'id',
            'user__username',
            'local_time',
            'test',
            'imputed',
            'available',
            'unavailable_reason',
            'treated',
            'treatment_probability',
            'sent_time',
            'received_time',
            'opened_time',
            'engaged_time',
            'message',
            'all_tags'
        ]


class WalkingSuggestionTimeFilters(admin.SimpleListFilter):
    title = 'Time Category'
    parameter_name = 'walking_suggestion_time_category'

    def lookups(self, request, model_admin):
        return SuggestionTime.CATEGORIES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__tag=self.value())
        else:
            return queryset

class WalkingSuggestionDecisionAdmin(ExportMixin, DecisionAdmin):
    resource_class = WalkingSuggestionDecisionResource

    list_filter = [WalkingSuggestionTimeFilters]
    list_display = ['decision', 'local_time', 'test', 'imputed', 'available', 'unavailable_reason', 'treated']

    def decision(self, decision):
        return '%s (%s)' % (decision.user.username, decision.category)

    def local_time(self, decision):
        local_datetime = decision.get_local_datetime()
        return local_datetime.strftime('%Y-%m-%d %H:%M')

admin.site.register(WalkingSuggestionDecision, WalkingSuggestionDecisionAdmin)

class WalkingSuggestionMessageTemplateAdmin(MessageTemplateAdmin):
    pass

admin.site.register(WalkingSuggestionMessageTemplate, WalkingSuggestionMessageTemplateAdmin)

def send_walking_suggestion(modeladmin, request, queryset):
    for configuration in queryset:
        category = random.choice(SuggestionTime.TIMES)
        decision_service = WalkingSuggestionDecisionService.create_decision(
            user = configuration.user,
            category = category,
            test = True
        )
        decision_service.update_context()
        decision_service.decide()
        decision_service.send_message()

def initialize_walking_suggestion_service(modeladmin, request, queryset):
    for configuration in queryset:
        try:
            service = WalkingSuggestionService(configuration=configuration)
            service.initialize()
            messages.add_message(request, messages.SUCCESS, 'Initialized %s' % (configuration.user.username))
        except WalkingSuggestionService.Unavailable:
            messages.add_message(request, messages.ERROR, 'Walking suggestion service unavailable for %s' % (configuration.user.username))
            continue
        except WalkingSuggestionService.UnableToInitialize:
            messages.add_message(request, messages.ERROR, 'Unable to initialize %s' % (configuration.user.username))
            continue

class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'enabled', 'service_initialized']
    exclude = ['day_start_hour', 'day_start_minute', 'day_end_hour', 'day_end_minute']
    readonly_fields = [
        'service_initialized_date',
        'walking_suggestion_times'
    ]
    actions = [send_walking_suggestion, initialize_walking_suggestion_service]

    def walking_suggestion_times(self, configuration):
        times = []
        for suggestion_time in configuration.suggestion_times:
            times.append('%s %s:%s' % (suggestion_time.category, suggestion_time.hour, suggestion_time.minute))
        if len(times) > 0:
            return ' '.join(times)
        else:
            return 'Not set'

admin.site.register(Configuration, ConfigurationAdmin)

admin.site.register(WalkingSuggestionServiceRequest, ServiceRequestAdmin)
