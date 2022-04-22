from django.db import models
import uuid

from participants.models import Study

# Create your models here.
class ReportType(models.Model):
    name = models.CharField(max_length=255)

class Report(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.ForeignKey(ReportType, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

class SupportingDataType(models.Model):
    name = models.CharField(max_length=255)

class SupportingData(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.ForeignKey(SupportingDataType, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(null=True)

class ReportSave(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete = models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    url = models.URLField(blank=True)

class ReportRecipients(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.ForeignKey(ReportType, on_delete = models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    recipient_email = models.TextField(blank=True)

class ReportDesign(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design = models.JSONField(default=dict)
    study = models.ForeignKey(Study, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

class ReportRenderLog(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_design = models.ForeignKey(ReportDesign, on_delete = models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, default='SUCCESS')
    log = models.JSONField(default=dict)