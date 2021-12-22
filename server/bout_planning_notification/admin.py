from django.contrib import admin

from surveys.admin import QuestionAdmin

from .models import BoutPlanningMessage, BoutPlanningSurveyQuestion, Configuration, FirstBoutPlanningTime, JSONSurvey, JustWalkJitaiDailyEmaQuestion, LevelSequence, LevelSequence_User, LevelSequenceBlock
from .models import BoutPlanningNotification, Level, BoutPlanningDecision

class FirstBoutPlanningTimeAdmin(admin.ModelAdmin):
    list_display = ['user', 'hour', 'minute', 'active']
    readonly_fields = ['user', 'hour', 'minute', 'active']

admin.site.register(FirstBoutPlanningTime, FirstBoutPlanningTimeAdmin)


class BoutPlanningNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'level', 'when']
    readonly_fields = ['user', 'message', 'level', 'decision', 'when']

admin.site.register(BoutPlanningNotification, BoutPlanningNotificationAdmin)



class LevelAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'date']
    readonly_fields = ['user', 'level', 'date']

admin.site.register(Level, LevelAdmin)


class BoutPlanningDecisionAdmin(admin.ModelAdmin):
    list_display = ['user', 'N', 'O', 'R', 'return_bool', 'when_created']
    readonly_fields = ['user', 'N', 'O', 'R', 'return_bool', 'when_created', 'data']
    
admin.site.register(BoutPlanningDecision, BoutPlanningDecisionAdmin)



class BoutPlanningSurveyConfigurationAdmin(admin.ModelAdmin):
    list_display = ['username', 'enabled']
    fields = ['user', 'enabled']

    def username(self, instance):
        return instance.user.username   

admin.site.register(Configuration, BoutPlanningSurveyConfigurationAdmin)

class BoutPlanningSurveyQuestionAdmin(QuestionAdmin):
    pass

admin.site.register(BoutPlanningSurveyQuestion, BoutPlanningSurveyQuestionAdmin)


class BoutPlanningMessageAdmin(admin.ModelAdmin):
    list_display = ['message']
    fields = ['message']

admin.site.register(BoutPlanningMessage, BoutPlanningMessageAdmin)


class JustWalkJitaiDailyEmaQuestionAdmin(QuestionAdmin):
    pass

admin.site.register(JustWalkJitaiDailyEmaQuestion, JustWalkJitaiDailyEmaQuestionAdmin)


class JSONSurveyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', 'updated']
    readonly_fields = ['uuid', 'created', 'updated']
    fields = ['name', 'structure']
    
admin.site.register(JSONSurvey, JSONSurveyAdmin)



class LevelSequenceAdmin(admin.ModelAdmin):
    list_display = ['cohort', 'order', 'is_used', 'when_created', 'when_used']
    fields = ['cohort', 'order', 'is_used', 'when_created', 'when_used', 'sequence_text']
    
admin.site.register(LevelSequence, LevelSequenceAdmin)

class LevelSequence_UserAdmin(admin.ModelAdmin):
    list_display = ['level_sequence','user', 'assigned']
    fields = ['level_sequence','user', 'assigned']

admin.site.register(LevelSequence_User, LevelSequence_UserAdmin)

def assign_level_sequences(modelAdmin, request, queryset):
    for block in queryset.all():
        lines = block.seq_block.split("\n")
        for line in lines:
            LevelSequence.create(cohort=block.cohort, sequence_text=line)

class LevelSequenceBlockAdmin(admin.ModelAdmin):
    actions = [assign_level_sequences]
    list_display = ['cohort', 'when_created', 'when_used']
    fields = ['cohort', 'seq_block']
    readonly_fields = ['when_created', 'when_used']
    
admin.site.register(LevelSequenceBlock, LevelSequenceBlockAdmin)
