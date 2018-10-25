from django.contrib import admin

from .models import ActivitySuggestionDecision, ActivityServiceRequest

class ActivitySuggestionDecisionAdmin(admin.ModelAdmin):
    pass
admin.site.register(ActivitySuggestionDecision, ActivitySuggestionDecisionAdmin)

class ActivityServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
admin.site.register(ActivityServiceRequest, ActivityServiceRequestAdmin)
