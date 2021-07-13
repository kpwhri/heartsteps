from django.contrib import admin
from .models import StepGoals, Days

class StepGoalsAdmin(admin.ModelAdmin):
    pass
admin.site.register(StepGoals, StepGoalsAdmin)
admin.site.register(Days)
