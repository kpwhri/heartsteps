from django.contrib import admin
from .models import StepGoal, StepGoalPRBScsv, StepGoalsEvidence

class StepGoalsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'step_goal', 'created']
    readonly_fields = ['uuid', 'user', 'date', 'step_goal', 'created']
    
admin.site.register(StepGoal, StepGoalsAdmin)


class StepGoalPRBScsvAdmin(admin.ModelAdmin):
    list_display = ['cohort', 'PRBS_text', 'when_created', 'delimiter']
    fields = ['cohort', 'PRBS_text', 'when_created', 'delimiter']
    
admin.site.register(StepGoalPRBScsv, StepGoalPRBScsvAdmin)


class StepGoalsEvidenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'startdate', 'enddate', 'base', 'created']
    readonly_fields = ['user', 'startdate', 'enddate', 'prev_startdate', 'prev_enddate', 'base', 
                       'magnitude', 'base_jump', 'maximum', 'minimum',     
                       'evidence', 'freetext', 'created']
    
admin.site.register(StepGoalsEvidence, StepGoalsEvidenceAdmin)