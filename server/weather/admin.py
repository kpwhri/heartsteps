from django.contrib import admin

from .models import DailyWeatherForecast

class DailyWeatherForecastAdmin(admin.ModelAdmin):
    pass
admin.site.register(DailyWeatherForecast, DailyWeatherForecastAdmin)

