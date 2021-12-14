from django.contrib import admin

from surveys.admin import QuestionAdmin

from .models import BoutPlanningSurveyQuestion, Configuration, FirstBoutPlanningTime
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
