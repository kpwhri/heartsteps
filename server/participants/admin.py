from django.contrib import admin
from .models import Participant

class ParticipantAdmin(admin.ModelAdmin):
    pass
admin.site.register(Participant, ParticipantAdmin)