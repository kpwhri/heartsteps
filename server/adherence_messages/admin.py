from django.conf import settings
from django.contrib import admin

from days.services import DayService

from .models import Configuration
from .models import AdherenceMessage
from .models import AdherenceMetric

class ConfigurationAdmin(admin.ModelAdmin):
    fields = [
        'user',
        'enabled',
        'daily_update'
    ]

    readonly_fields = [
        'daily_update'
    ]

    ordering = ['user__username']

    def daily_update(self, instance):
        if instance.daily_task:
            next_run_datetime = instance.daily_task.get_next_run_time()
            day_service = DayService(user = instance.user)
            timezone = day_service.get_timezone_at(next_run_datetime)
            corrected_datetime = next_run_datetime.astimezone(timezone)
            if next_run_datetime:
                return 'Next update at %s (%s)' % (corrected_datetime.strftime('%Y-%m-%d %H:%M'), timezone.zone)
        else:
            return 'No daily update'

admin.site.register(Configuration, ConfigurationAdmin)

class AdherenceMessageAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'created',
        'category',
        'body'
    ]
    fields = [
        'user',
        'category',
        'body'
    ]
    readonly_fields = [
        'user',
        'category',
        'body'
    ]
    ordering = ['-created', 'user__username']

admin.site.register(AdherenceMessage, AdherenceMessageAdmin)

class AdherenceMetricAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'date',
        'value'
    ]
    ordering = ['-date', 'user__username']

admin.site.register(AdherenceMetric, AdherenceMetricAdmin)
