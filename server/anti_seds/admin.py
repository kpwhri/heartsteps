from django.contrib import admin

from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin

from .models import AntiSedentaryMessageTemplate, AntiSedentaryDecision

class AntiSedentaryDecisionAdmin(DecisionAdmin):
    pass
admin.site.register(AntiSedentaryDecision, AntiSedentaryDecisionAdmin)

class AntiSedentaryMessageTemplateAdmin(MessageTemplateAdmin):
    pass
admin.site.register(AntiSedentaryMessageTemplate, AntiSedentaryMessageTemplateAdmin)
