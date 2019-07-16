from django.contrib import admin

from .models import AdherenceMetric
from .models import Configuration

class AdherenceMetricAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'date',
        'value'
    ]
    ordering = ['-date', 'user__username']

admin.site.register(AdherenceMetric, AdherenceMetricAdmin)

class ConfigurationAdmin(admin.ModelAdmin):
    fields = [
        'user',
        'enabled'
    ]
admin.site.register(Configuration, ConfigurationAdmin)
