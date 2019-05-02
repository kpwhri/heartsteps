from datetime import timedelta

from django.contrib import admin

from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field

from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin
from randomization.resources import DecisionResource
from service_requests.admin import ServiceRequestAdmin

from .models import Configuration, AntiSedentaryMessageTemplate, AntiSedentaryDecision, AntiSedentaryServiceRequest
from .services import AntiSedentaryDecisionService, AntiSedentaryService, FitbitStepCountService

def send_anti_sedentary_message(admin, request, queryset):
    for configuration in queryset.all():
        decision_service = AntiSedentaryDecisionService.create_decision(
            user = configuration.user,
            test = True
        )
        decision_service.decide()
        decision_service.update_context()
        decision_service.send_message()


class AntiSedentaryConfigurationAdmin(ExportMixin, admin.ModelAdmin):
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


def get_step_count(decision):
    service = AntiSedentaryService(user=decision.user)
    try:
        return service.get_step_count_at(decision.time)
    except AntiSedentaryService.NoSteps:
        return None

def get_fitbit_step_count(decision):
    service = FitbitStepCountService(user = decision.user)
    return service.get_step_count_between(
        start = decision.time - timedelta(minutes=40),
        end = decision.time
    )

class AntiSedentaryDecisionResouce(DecisionResource):

    step_count = Field()
    fitbit_step_count = Field()

    class Meta:
        model = AntiSedentaryDecision

        fields = [
            'id',
            'user__username',
            'local_time',
            'step_count',
            'fitbit_step_count',
            'test',
            'imputed',
            'available',
            'unavailable_reason',
            'treated',
            'treatment_probability',
            'sent_time',
            'received_time',
            'opened_time',
            'engaged_time',
            'message',
            'all_tags'
        ]

        export_order = [
            'id',
            'user__username',
            'local_time',
            'step_count',
            'fitbit_step_count',
            'test',
            'imputed',
            'available',
            'unavailable_reason',
            'treated',
            'treatment_probability',
            'sent_time',
            'received_time',
            'opened_time',
            'engaged_time',
            'message',
            'all_tags'
        ]

    def dehydrate_step_count(self, decision):
        return get_step_count(decision)

    def dehydrate_fitbit_step_count(self, decision):
        return get_fitbit_step_count(decision)


class AntiSedentaryDecisionAdmin(ExportMixin, DecisionAdmin):
    resource_class = AntiSedentaryDecisionResouce
    list_display = ['user', 'local_time', 'step_count', 'fitbit_step_count', 'sedentary', 'available', 'treated', 'imputed', 'test']

    def local_time(self, decision):
        return decision.get_local_datetime().strftime('%Y-%m-%d %I:%M %p')

    def step_count(self, decision):
        return get_step_count(decision)

    def fitbit_step_count(self, decision):
        return get_fitbit_step_count(decision)

admin.site.register(AntiSedentaryDecision, AntiSedentaryDecisionAdmin)


class AntiSedentaryMessageTemplateAdmin(MessageTemplateAdmin):
    pass
admin.site.register(AntiSedentaryMessageTemplate, AntiSedentaryMessageTemplateAdmin)

admin.site.register(AntiSedentaryServiceRequest, ServiceRequestAdmin)
