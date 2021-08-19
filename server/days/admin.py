from django.contrib import admin

from .models import Day

class DayAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'timezone', 'start', 'end']
    fields = ['user', 'date', 'timezone', 'start', 'end']

admin.site.register(Day, DayAdmin)
