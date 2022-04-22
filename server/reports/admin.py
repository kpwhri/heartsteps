from django.contrib import admin

from .models import ReportType, Report, SupportingDataType, SupportingData, ReportSave, ReportRecipients

# Register your models here.


admin.site.register([ReportType, Report, SupportingDataType, SupportingData, ReportSave, ReportRecipients])