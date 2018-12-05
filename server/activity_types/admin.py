from django.contrib import admin
from .models import ActivityType

class ActivityTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(ActivityType, ActivityTypeAdmin)
