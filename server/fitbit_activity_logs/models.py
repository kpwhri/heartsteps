from django.db import models

from activity_logs.models import ActivityType
from fitbit_api.models import FitbitActivityType

class FitbitActivityToActivityType(models.Model):
    fitbit_activity = models.OneToOneField(FitbitActivityType)
    activity_type = models.ForeignKey(ActivityType)
