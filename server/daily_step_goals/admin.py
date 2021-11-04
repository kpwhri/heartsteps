from django.contrib import admin
from .models import StepGoal

class StepGoalsAdmin(admin.ModelAdmin):
    pass
admin.site.register(StepGoal, StepGoalsAdmin)
