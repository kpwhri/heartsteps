from django.contrib import admin

from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin

from .models import SuggestionTime, Configuration, ActivitySuggestionDecision, ActivitySuggestionMessageTemplate

class ActivitySuggestionTimeFilters(admin.SimpleListFilter):
    title = 'Time Category'
    parameter_name = 'activity_suggestion_time_category'

    def lookups(self, request, model_admin):
        return SuggestionTime.CATEGORIES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__tag=self.value())
        else:
            return queryset

class ActivitySuggestionDecisionAdmin(DecisionAdmin):
    list_filter = [ActivitySuggestionTimeFilters]
admin.site.register(ActivitySuggestionDecision, ActivitySuggestionDecisionAdmin)

class ActivitySuggestionMessageTemplateAdmin(MessageTemplateAdmin):
    pass
admin.site.register(ActivitySuggestionMessageTemplate, ActivitySuggestionMessageTemplateAdmin)

class ConfigurationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Configuration, ConfigurationAdmin)
