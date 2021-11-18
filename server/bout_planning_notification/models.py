# from datetime import timedelta

# from django.utils import timezone

from django.db import models
from django.contrib.auth import get_user_model

# from daily_tasks.models import DailyTask

User = get_user_model()

from django.db import models

# Create your models here.


class FirstBoutPlanningTime(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    time = models.CharField(max_length=15)

    active = models.BooleanField(default=True)

    @property
    def formatted_time(self):
        if self.time:
            return "%s" % (self.time)
        else:
            return "Unset"

    @property
    def hour(self):
        return int(self.time.split(':')[0])

    @property
    def minute(self):
        return int(self.time.split(':')[1])