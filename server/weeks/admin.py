from django.contrib import admin
from django.contrib import messages

from surveys.admin import QuestionAdmin

from .models import Week
from .models import WeeklyBarrierOption
from .models import WeekQuestion
from .services import WeekService

def send_reflection(modeladmin, request, queryset):
    for week in queryset.all():
        service = WeekService(user = week.user)
        service.send_reflection(week, test=True)
        messages.add_message(
            request,
            messages.SUCCESS,
            'Sent weekly reflection to %s' % (week.user.username)
        )

class WeekAdmin(admin.ModelAdmin):
    ordering = ['-start_date']
    list_display = ['user', 'number', 'start_date', 'end_date']
    fields = ['user', 'number', 'goal']
    readonly_fields = ['uuid', 'user', 'number', 'start_date', 'end_date', 'goal']

    actions = [send_reflection]

    def goal(admin, week):
        if week.minutes:
            goal = WeeklyGoal.objects.get(week=week)
            return "%d minutes (%d)" % (goal.minutes, goal.confidence*100)
        else:
            return "No set"


admin.site.register(Week, WeekAdmin)

class WeekQuestionAdmin(QuestionAdmin):
    pass

admin.site.register(WeekQuestion, WeekQuestionAdmin)

class WeeklyBarrierOptionAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = [
        'name',
        'user'
    ]
    fields = [
        'name',
        'user'
    ]
    readonly_fields = [
        'user'
    ]

admin.site.register(WeeklyBarrierOption, WeeklyBarrierOptionAdmin)
