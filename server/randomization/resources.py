from import_export import resources
from import_export.fields import Field
from import_export.admin import ExportMixin

class DecisionResource(resources.ModelResource):

    local_time = Field(column_name='time')
    all_tags = Field(column_name='tags')
    sent_time = Field()
    received_time = Field()
    opened_time = Field()
    engaged_time = Field()
    message = Field()

    def format_datetime(self, time):
        if time:
            return time.strftime('%Y-%m-%d %H:%M %z')
        else:
            return ''

    def dehydrate_local_time(self, decision):
        time = decision.get_local_datetime()
        return self.format_datetime(time)
    
    def dehydrate_all_tags(self, decision):
        return ', '.join(decision.get_context())

    def dehydrate_sent_time(self, decision):
        if decision.notification:
            return self.format_datetime(decision.notification.sent)
        else:
            return ''

    def dehydrate_received_time(self, decision):
        if decision.notification:
            return self.format_datetime(decision.notification.received)
        else:
            return ''

    def dehydrate_opened_time(self, decision):
        if decision.notification:
            return self.format_datetime(decision.notification.opened)
        else:
            return ''

    def dehydrate_engaged_time(self, decision):
        if decision.notification:
            return self.format_datetime(decision.notification.engaged)
        else:
            return ''

    def dehydrate_message(self, decision):
        if decision.message_template:
            return decision.message_template.body
        else:
            return ''
