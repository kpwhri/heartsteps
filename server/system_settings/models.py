from django.db import models

# Create your models here.
from participants.models import Study

class SystemSetting(models.Model):
    key = models.CharField(max_length=500, primary_key=True)
    value = models.TextField()

    def get(key):
        try:
            return SystemSetting.objects.get(key=key).value
        except SystemSetting.DoesNotExist:
            return ""

    def __str__(self):
        return "SystemSetting: {}={}".format(self.key, self.value)

class StudySetting(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    key = models.CharField(max_length=500, primary_key=True)
    value = models.TextField()

    def get(study, key):
        try:
            return StudySetting.objects.get(study=study, key=key).value
        except StudySetting.DoesNotExist:
            return ""

    def __str__(self):
        return "StudySetting({}): {}={}".format(self.study.name, self.key, self.value)