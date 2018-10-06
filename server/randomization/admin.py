from django.contrib import admin
from django.db import models

from randomization.models import ContextTag, UserRandomization, Decision
from push_messages.models import MessageReceipt

@admin.register(ContextTag)
class ContextTagAdmin(admin.ModelAdmin):
    pass

@admin.register(UserRandomization)
class UserRandomizationAdmin(admin.ModelAdmin):
    
    # date_hierarchy = 'created'
    change_list_template = 'admin/user_randomization_change_list.html'

    def make_decision_metrics(self, tag=None):
        if not tag:
            name = "All"
            total = Decision.objects.count()
            total_treated = Decision.objects.filter(a_it=True).count()
            receipts_query = MessageReceipt.objects.filter(message__randomization_message__decision__a_it=True)
        else:
            name = str(tag)
            total = Decision.objects.filter(tags=tag).count()
            total_treated = Decision.objects.filter(tags=tag, a_it=True).count()
            receipts_query = MessageReceipt.objects.filter(message__randomization_message__decision__a_it=True, message__randomization_message__decision__tags=tag)

        sent = receipts_query.filter(type=MessageReceipt.SENT).count()
        received = receipts_query.filter(type=MessageReceipt.RECEIVED).count()
        opened = receipts_query.filter(type=MessageReceipt.OPENED).count()
        engaged = receipts_query.filter(type=MessageReceipt.ENGAGED).count()

        return {
                'name': name,
                'total': total,
                'treated': total_treated,
                'sent': sent,
                'received': received,
                'opened': opened,
                'engaged': engaged
        }

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context
        )

        decision_metrics = [
            self.make_decision_metrics()
        ]
        for tag in ContextTag.objects.filter(dashboard=True):
            decision_metrics.append(self.make_decision_metrics(tag))
        response.context_data['decision_metrics'] = decision_metrics

        return response
