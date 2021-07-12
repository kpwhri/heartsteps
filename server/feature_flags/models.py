from django.db import models
from django.conf import settings
import uuid


class FeatureFlags(models.Model):
    class Meta:
        verbose_name = 'Feature Flags'
        verbose_name_plural = 'Feature Flags'

    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    notification_center_flag = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
