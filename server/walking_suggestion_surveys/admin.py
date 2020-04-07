from django.contrib import admin

from surveys.admin import QuestionAdmin

from .models import Configuration
from .models import WalkingSuggestionSurvey
from .models import WalkingSuggestionSurveyQuestion

class WalkingSuggestionSurveyConfigurationAdmin(admin.ModelAdmin):
    list_display = ['username', 'enabled']
    fields = ['user', 'enabled']

    def username(self, instance):
        return instance.user.username   

admin.site.register(Configuration, WalkingSuggestionSurveyConfigurationAdmin)

class WalkingSuggestionQuestionAdmin(QuestionAdmin):
    pass

admin.site.register(WalkingSuggestionSurveyQuestion, WalkingSuggestionQuestionAdmin)
