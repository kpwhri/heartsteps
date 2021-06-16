from django.contrib import admin
from .models import StepGoals

class StepGoalsAdmin(admin.ModelAdmin):
    pass
admin.site.register(StepGoals, StepGoalsAdmin)
