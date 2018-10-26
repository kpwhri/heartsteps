from django.contrib import admin

from .models import SuggestionTime, SuggestionTimeConfiguration, ActivitySuggestionDecision, ActivitySuggestionServiceRequest, TIME_CATEGORIES

class ActivitySuggestionTimeFilters(admin.SimpleListFilter):
    title = 'Time Category'
    parameter_name = 'activity_suggestion_time_category'

    def lookups(self, request, model_admin):
        return TIME_CATEGORIES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__tag=self.value())
        else:
            return queryset

class ActivitySuggestionDecisionAdmin(admin.ModelAdmin):
    date_hierarchy = 'time'
    search_fields = [
        'user__username'
    ]
    list_filter = [ActivitySuggestionTimeFilters]
admin.site.register(ActivitySuggestionDecision, ActivitySuggestionDecisionAdmin)

class SuggestionTimeInlineAdmin(admin.TabularInline):
    model = SuggestionTime
    extra = 0
    can_delete = False
    fields = ('type', 'hour', 'minute')


class SuggestionTimeConfigurationAdmin(admin.ModelAdmin):
    inlines = [
        SuggestionTimeInlineAdmin
    ]
admin.site.register(SuggestionTimeConfiguration, SuggestionTimeConfigurationAdmin)

class ActivitySuggestionServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
admin.site.register(ActivitySuggestionServiceRequest, ActivitySuggestionServiceRequestAdmin)
