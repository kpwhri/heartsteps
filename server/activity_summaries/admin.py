from django.contrib import admin
from .models import Day

class DayAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'steps', 'miles', 'activities_completed', 'moderate_minutes', 'vigorous_minutes', 'total_minutes', 'updated']
    readonly_fields = ['user', 'date', 'steps', 'miles', 'activities_completed', 'moderate_minutes', 'vigorous_minutes', 'total_minutes', 'updated']

admin.site.register(Day, DayAdmin)