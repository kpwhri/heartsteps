from django.contrib import admin
from django.contrib.auth.models import User, Group

from rest_framework.authtoken.models import Token
from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule

from participants.models import Participant

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Token)
admin.site.unregister(TaskResult)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(PeriodicTask)

class ParticipantAdmin(admin.ModelAdmin):
    pass
admin.site.register(Participant, ParticipantAdmin)