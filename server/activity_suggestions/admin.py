from django.contrib import admin

from .models import SuggestionTime, Configuration, ActivitySuggestionDecision, ServiceRequest

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

class ActivitySuggestionDecisionAdmin(admin.ModelAdmin):
    date_hierarchy = 'time'
    search_fields = [
        'user__username'
    ]
    list_filter = [ActivitySuggestionTimeFilters]
admin.site.register(ActivitySuggestionDecision, ActivitySuggestionDecisionAdmin)

class ConfigurationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Configuration, ConfigurationAdmin)

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
