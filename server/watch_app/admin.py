from django.contrib import admin

from .models import StepCount

class StepCountAdmin(admin.ModelAdmin):
    pass

admin.site.register(StepCount, StepCountAdmin)
