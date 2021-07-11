from django.db import models
from django.contrib.auth.models import User
import uuid


class FeatureFlags(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    notification_center_flag = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
