from django.contrib import admin
from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin

from .models import Configuration, AntiSedentaryMessageTemplate, AntiSedentaryDecision
from .services import AntiSedentaryDecisionService

def send_anti_sedentary_message(admin, request, queryset):
    for configuration in queryset.all():
        decision_service = AntiSedentaryDecisionService.create_decision(
            user = configuration.user,
            test = True
        )
        decision_service.decide()
        decision_service.update_context()
        decision_service.send_message()

class AntiSedentaryConfigurationAdmin(admin.ModelAdmin):
    list_display = ['user', 'enabled']
    actions = [send_anti_sedentary_message]
    readonly_fields = [
        'last_sedentary_decision'
    ]

    def last_sedentary_decision(self, configuration):
        decision = AntiSedentaryDecision.objects.filter(
            user = configuration.user,
            imputed = False,
            test = False
        ).first()
        if not decision:
            return 'No anti-sedentary decision'
        time_formatted = decision.time.strftime('%Y-%m-%d at %H:%M')
        if decision.treated:
            return 'Treated on %s' % (time_formatted)
        else:
            return 'Not treated on %s' % (time_formatted)


admin.site.register(Configuration, AntiSedentaryConfigurationAdmin)

class AntiSedentaryDecisionAdmin(DecisionAdmin):
    list_display = ['user', 'time', 'sedentary', 'available', 'treated', 'imputed', 'test']
    pass
admin.site.register(AntiSedentaryDecision, AntiSedentaryDecisionAdmin)

class AntiSedentaryMessageTemplateAdmin(MessageTemplateAdmin):
    pass
admin.site.register(AntiSedentaryMessageTemplate, AntiSedentaryMessageTemplateAdmin)
