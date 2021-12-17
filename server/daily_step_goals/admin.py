from django.contrib import admin
from .models import StepGoal, StepGoalPRBScsv

class StepGoalsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'step_goal']
    readonly_fields = ['uuid', 'user', 'date', 'step_goal']
    
admin.site.register(StepGoal, StepGoalsAdmin)


class StepGoalPRBScsvAdmin(admin.ModelAdmin):
    list_display = ['cohort', 'PRBS_text', 'when_created', 'delimiter']
    fields = ['cohort', 'PRBS_text', 'when_created', 'delimiter']
    
admin.site.register(StepGoalPRBScsv, StepGoalPRBScsvAdmin)