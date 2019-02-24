from django.contrib import admin

from push_messages.models import Message

class MessageAdmin(admin.ModelAdmin):
    ordering = ['-created']
    list_display = ['__str__', 'created']

    readonly_fields = [
        'message_type',
        'recipient',
        'device',
        'content',
        'sent',
        'received',
        'opened',
        'engaged'
        ]

admin.site.register(Message, MessageAdmin)
