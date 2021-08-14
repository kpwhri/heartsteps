from django.contrib import admin

from .models import Day

admin.site.register(Day, admin.ModelAdmin)
