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
    pass
admin.site.register(Configuration, ConfigurationAdmin)
