import random

from django.contrib import admin

from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin
from service_requests.admin import ServiceRequestAdmin

from walking_suggestion_times.models import SuggestionTime

from walking_suggestions.models import SuggestionTime, Configuration
from walking_suggestions.models import WalkingSuggestionDecision, WalkingSuggestionMessageTemplate
from walking_suggestions.models import WalkingSuggestionServiceRequest
from walking_suggestions.services import WalkingSuggestionDecisionService

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

class WalkingSuggestionDecisionAdmin(DecisionAdmin):
    list_filter = [WalkingSuggestionTimeFilters]
    list_display = ['decision', 'time', 'available', 'treated']

    def decision(self, decision):
        return '%s (%s)' % (decision.user.username, decision.category)

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

class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'enabled', 'service_initialized']
    exclude = ['day_start_hour', 'day_start_minute', 'day_end_hour', 'day_end_minute']
    readonly_fields = [
        'service_initialized_date',
        'walking_suggestion_times'
    ]
    actions = [send_walking_suggestion]

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
