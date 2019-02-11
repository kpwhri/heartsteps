from django.contrib import admin

from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin

from walking_suggestion_times.models import SuggestionTime

from .models import SuggestionTime, Configuration, WalkingSuggestionDecision, WalkingSuggestionMessageTemplate

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

admin.site.register(WalkingSuggestionDecision, WalkingSuggestionDecisionAdmin)

class WalkingSuggestionMessageTemplateAdmin(MessageTemplateAdmin):
    pass

admin.site.register(WalkingSuggestionMessageTemplate, WalkingSuggestionMessageTemplateAdmin)

class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'enabled', 'service_initialized']
    exclude = ['day_start_hour', 'day_start_minute', 'day_end_hour', 'day_end_minute']
    readonly_fields = [
        'service_initialized_date',
        'walking_suggestion_times',
        'next_walking_suggestion_time'
    ]

    def walking_suggestion_times(self, configuration):
        times = []
        for suggestion_time in configuration.suggestion_times:
            times.append('%s %s:%s' % (suggestion_time.category, suggestion_time.hour, suggestion_time.minute))
        if len(times) > 0:
            return ' '.join(times)
        else:
            return 'Not set'
    
    def next_walking_suggestion_time(self, configuration):
        try:
            next_run = configuration.get_next_suggestion_time()
            return next_run.strftime('%Y-%m-%d %H:%M')
        except RuntimeError:
            return 'None'

admin.site.register(Configuration, ConfigurationAdmin)
