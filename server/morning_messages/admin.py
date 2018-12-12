from django.contrib import admin

from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin

from .models import MorningMessageTemplate, MorningMessageDecision

class MorningMessageDecisionAdmin(DecisionAdmin):
    pass
admin.site.register(MorningMessageDecision, MorningMessageDecisionAdmin)

class MorningMessageTemplateAdmin(MessageTemplateAdmin):
    pass
admin.site.register(MorningMessageTemplate, MorningMessageTemplateAdmin)
