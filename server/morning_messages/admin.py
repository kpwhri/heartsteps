from django.contrib import admin
from django.contrib import messages

from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin

from .models import Configuration, MorningMessageTemplate, MorningMessageDecision
from .services import MorningMessageService

def send_morning_message(modeladmin, request, queryset):
    for configuration in queryset.all():
        service = MorningMessageService(configuration = configuration)
        service.send_notification(test=True)
        messages.add_message(
            request,
            messages.SUCCESS, 
            'Sent morning message to %s' % (configuration.user.username)
            )

class MorningMessageConfigurationAdmin(admin.ModelAdmin):
    list_display = ['username', 'enabled']
    fields = ['user', 'enabled', 'next_morning_message']
    readonly_fields = ['user', 'next_morning_message']
    actions = [send_morning_message]

    def username(self, instance):
        return instance.user.username

    def next_morning_message(self, instance):
        if instance.enabled:
            return instance.daily_task.get_next_run_time().strftime('%Y-%m-%d %H:%M')
        else:
            return 'Morning message not enabled'

admin.site.register(Configuration, MorningMessageConfigurationAdmin)

class MorningMessageDecisionAdmin(DecisionAdmin):
    pass
admin.site.register(MorningMessageDecision, MorningMessageDecisionAdmin)

class MorningMessageTemplateAdmin(MessageTemplateAdmin):
    pass
admin.site.register(MorningMessageTemplate, MorningMessageTemplateAdmin)
