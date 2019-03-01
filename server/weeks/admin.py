from django.contrib import admin

from .models import Week

class WeekAdmin(admin.ModelAdmin):
    ordering = ['-start_date']
    list_display = ['user', 'number', 'start_date', 'end_date']
    readonly_fields = ['uuid', 'user', 'number', 'start_date', 'end_date']
admin.site.register(Week, WeekAdmin)
