from django.contrib import admin

from .models import Contact
from .models import Message

class ContactAdmin(admin.ModelAdmin):
    list_display = ['user', 'number', 'enabled']

admin.site.register(Contact, ContactAdmin)

class MessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'recipient', 'sender', 'body', 'created']

    readonly_fields = [
        'recipient',
        'sender',
        'body',
        'created'
        ]

admin.site.register(Message, MessageAdmin)
