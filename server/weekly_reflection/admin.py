from django.contrib import admin

from weeks.models import Week
from weekly_goals.models import WeeklyGoal

from .models import ReflectionTime
from .tasks import send_reflection

def send_weekly_reflection(admin, request, queryset):
    for reflection_time in queryset:
        send_reflection(reflection_time.user.username)

class WeeklyReflectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'formatted_time', 'active']
    fields = ['user', 'day', 'time', 'active', 'next_run']
    readonly_fields = ['user', 'next_run']
    actions = [send_weekly_reflection]

    def next_run(self, reflection_time):
        next_run = reflection_time.get_next_time()
        return next_run.strftime('%Y-%m-%d %H:%M')

admin.site.register(ReflectionTime, WeeklyReflectionAdmin)

class WeekAdmin(admin.ModelAdmin):
    ordering = ['-start_date']
    list_display = ['user', 'number', 'start_date', 'end_date']
    fields = ['user', 'number', 'goal']
    readonly_fields = ['uuid', 'user', 'number', 'start_date', 'end_date', 'goal']

    def goal(admin, week):
        try:
            goal = WeeklyGoal.objects.get(week=week)
            return "%d minutes (%d)" % (goal.minutes, goal.confidence*100)
        except WeeklyGoal.DoesNotExist:
            return "Not found"


admin.site.register(Week, WeekAdmin)
