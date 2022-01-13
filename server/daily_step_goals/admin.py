from django.contrib import admin
from .models import StepGoal, StepGoalSequence, StepGoalSequence_User, StepGoalSequenceBlock, StepGoalsEvidence

class StepGoalsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'step_goal', 'created']
    readonly_fields = ['uuid', 'user', 'date', 'step_goal', 'created']
    
admin.site.register(StepGoal, StepGoalsAdmin)


class StepGoalSequenceBlockAdmin(admin.ModelAdmin):
    list_display = ['cohort', 'when_created', 'when_used']
    fields = ['cohort', 'seq_block']
    readonly_fields = ['when_created', 'when_used']

admin.site.register(StepGoalSequenceBlock, StepGoalSequenceBlockAdmin)

class StepGoalSequenceAdmin(admin.ModelAdmin):
    list_display = ['cohort', 'order', 'is_used', 'when_created', 'when_used', 'sequence_text']
    fields = ['cohort', 'order', 'is_used', 'sequence_text']
    readonly_fields = ['when_created', 'when_used']

admin.site.register(StepGoalSequence, StepGoalSequenceAdmin)

class StepGoalSequence_UserAdmin(admin.ModelAdmin):
    list_display = ['user', 'step_goal_sequence', 'assigned']
    fields = ['user', 'step_goal_sequence']
    readonly_fields = ['assigned']

admin.site.register(StepGoalSequence_User, StepGoalSequence_UserAdmin)


class StepGoalsEvidenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'startdate', 'enddate', 'base', 'created']
    readonly_fields = ['user', 'startdate', 'enddate', 'prev_startdate', 'prev_enddate', 'base', 
                       'magnitude', 'base_jump', 'maximum', 'minimum',     
                       'evidence', 'freetext', 'created']
    
admin.site.register(StepGoalsEvidence, StepGoalsEvidenceAdmin)