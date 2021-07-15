from django.contrib import admin
from .models import StepGoal, ActivityDay

class StepGoalsAdmin(admin.ModelAdmin):
    pass
admin.site.register(StepGoal, StepGoalsAdmin)
admin.site.register(ActivityDay)
