from datetime import timedelta

from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.utils import timezone

from days.services import DayService

from .models import Configuration
from .models import AdherenceMessage
from .models import AdherenceMetric
from .services import AdherenceService
from .tasks import initialize_adherence
from .tasks import update_adherence

def initialize_configuration(modeladmin, request, queryset):
    for configuration in queryset.all():
        initialize_adherence.apply_async(kwargs = {
            'username': configuration.user.username
        })
        messages.add_message(request, messages.INFO, 'Queued initialization for %s' % (configuration.user.username))

def send_adherence_message(modeladmin, request, queryset):
    for configuration in queryset.all():
        try:
            service = AdherenceService(configuration = configuration)
            service.send_adherence_message()
            messages_sent = AdherenceMessage.objects.filter(
                user = configuration.user,
                created__gte = timezone.now() - timedelta(minutes=2)
            ).count()
            if messages_sent:
                messages.add_message(request, messages.INFO, 'Adherence message sent to %s' % (configuration.user.username))
            else:
                messages.add_message(request, messages.INFO, 'No adherence messages sent to %s' % (configuration.user.username))
        except:
            messages.add_message(request, messages.ERROR, 'Error while sending adherence message to %s' % (configuration.user.username))

def update_adherence_metrics(modeladmin, request, queryset):
    for configuration in queryset.all():
        update_adherence.apply_async(kwargs = {
            'username': configuration.user.username
        })
        messages.add_message(request, messages.INFO, 'Queued adherence update for %s' % (configuration.user.username))

class ConfigurationAdmin(admin.ModelAdmin):

    actions = [
        initialize_configuration,
        send_adherence_message,
        update_adherence_metrics
    ]

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
