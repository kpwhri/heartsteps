from django.contrib import admin

from surveys.admin import QuestionAdmin

from .models import Configuration
from .models import ActivitySurvey
from .models import ActivitySurveyQuestion

class ActivitySurveyConfigurationAdmin(admin.ModelAdmin):
    list_display = ['username', 'enabled']
    fields = ['user', 'enabled']

    def username(self, instance):
        return instance.user.username   

admin.site.register(Configuration, ActivitySurveyConfigurationAdmin)

class ActivitySurveyQuestionAdmin(QuestionAdmin):
    pass

admin.site.register(ActivitySurveyQuestion, ActivitySurveyQuestionAdmin)
