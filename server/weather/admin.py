from django.contrib import admin

from .models import DailyWeatherForecast
from .models import ZipCodeInfo

class DailyWeatherForecastAdmin(admin.ModelAdmin):
    pass

# class ZipCodeInfo(admin.ModelAdmin):
#     list_display = ['user', 'app_key']
#     fields = ['user', 'app_key']

admin.site.register(DailyWeatherForecast, DailyWeatherForecastAdmin)
admin.site.register(ZipCodeInfo)

