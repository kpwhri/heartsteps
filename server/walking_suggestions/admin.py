import random
import datetime

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
from walking_suggestions.models import PoolingServiceConfiguration
from walking_suggestions.models import PoolingServiceRequest
from walking_suggestions.services import WalkingSuggestionDecisionService
from walking_suggestions.services import WalkingSuggestionService
from walking_suggestions.tasks import initialize_and_update

class WalkingSuggestionDecisionResource(DecisionResource):

    class Meta:
        model = WalkingSuggestionDecision
        fields = DecisionResource.FIELDS
        export_order = DecisionResource.FIELDS


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
    list_display = ['decision', 'local_time', 'test', 'imputed', 'treated']

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
        initialize_and_update.apply_async(
            kwargs = {
                'username': configuration.user.username
            }
        )
        messages.add_message(request, messages.INFO, 'Queued initialization for %s' % (configuration.user.username))

class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'enabled', 'service_initialized']
    exclude = ['day_start_hour', 'day_start_minute', 'day_end_hour', 'day_end_minute']
    readonly_fields = [
        'service_initialized_date',
        'walking_suggestion_times'
    ]
    actions = [
        send_walking_suggestion,
        initialize_walking_suggestion_service
    ]

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

class PoolingServiceConfigurationAdmin(admin.ModelAdmin):
    list_display = ['user', 'use_pooling']
admin.site.register(PoolingServiceConfiguration, PoolingServiceConfigurationAdmin)

admin.site.register(PoolingServiceRequest, ServiceRequestAdmin)
