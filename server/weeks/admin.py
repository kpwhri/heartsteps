from django.contrib import admin

from .models import Week

class WeekAdmin(admin.ModelAdmin):
    ordering = ['-start_date']
    list_display = ['user', 'number', 'start_date', 'end_date']
    fields = ['user', 'number', 'goal']
    readonly_fields = ['uuid', 'user', 'number', 'start_date', 'end_date', 'goal']

    def goal(admin, week):
        if week.minutes:
            goal = WeeklyGoal.objects.get(week=week)
            return "%d minutes (%d)" % (goal.minutes, goal.confidence*100)
        else:
            return "No set"


admin.site.register(Week, WeekAdmin)
