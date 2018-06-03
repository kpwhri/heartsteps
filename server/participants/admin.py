from django.contrib import admin
from participants.models import Participant

class ParticipantAdmin(admin.ModelAdmin):
    pass
admin.site.register(Participant, ParticipantAdmin)