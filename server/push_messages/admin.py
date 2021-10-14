from django.contrib import admin

from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field

from push_messages.models import Message, Device, OneSignalInfo

message_resource_fields = [
    'id',
    'username',
    'message_type',
    'content',
    'sent',
    'received',
    'opened',
    'engaged'
]

class MessageResource(resources.ModelResource):

    id = Field()
    username = Field()
    sent = Field()
    received = Field()
    opened = Field()
    engaged = Field()

    class Meta:
        model = Message
        fields = message_resource_fields
        export_order = message_resource_fields

    def dehydrate_id(self, message):
        return str(message.uuid)
    
    def dehydrate_username(self, message):
        return message.recipient.username

    def format_time(self, time):
        if time:
            return time.strftime('%Y-%m-%d %H:%M %z')
        else:
            return ''

    def dehydrate_sent(self, message):
        return self.format_time(message.sent)

    def dehydrate_received(self, message):
        return self.format_time(message.received)

    def dehydrate_opened(self, message):
        return self.format_time(message.opened)

    def dehydrate_engaged(self, message):
        return self.format_time(message.engaged)

class MessageAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = MessageResource
    ordering = ['-created']
    list_display = ['__str__', 'body', 'created']

    search_fields = [
        'recipient__username'
    ]

    readonly_fields = [
        'message_type',
        'recipient',
        'device',
        'title',
        'body',
        'data',
        'sent',
        'received',
        'opened',
        'engaged'
        ]

admin.site.register(Message, MessageAdmin)

admin.site.register(Device, admin.ModelAdmin)

class OneSignalInfoAdmin(admin.ModelAdmin):
    list_display = ['study', 'app_id', 'app_key']
    fields = ['study', 'app_id', 'app_key']

admin.site.register(OneSignalInfo, OneSignalInfoAdmin)