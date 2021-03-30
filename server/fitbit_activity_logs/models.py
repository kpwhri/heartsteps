from django.db import models

from activity_logs.models import ActivityType
from fitbit_activities.models import FitbitActivityType

class FitbitActivityToActivityType(models.Model):
    fitbit_activity_type = models.OneToOneField(FitbitActivityType, on_delete = models.CASCADE)
    activity_type = models.ForeignKey(ActivityType, on_delete = models.CASCADE)
