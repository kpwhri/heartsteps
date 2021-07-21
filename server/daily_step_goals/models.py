from django.db import models

from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

# from activity_summaries.models import Day
from activity_summaries import models as activity_summaries_models

# Create your models here.
class StepGoal(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    date = models.DateField()
    step_goal = models.PositiveIntegerField()

    @property
    def id(self):
        return str(self.uuid)

class ActivityDay(models.Model):
    day = models.ForeignKey(activity_summaries_models.Day, on_delete = models.CASCADE)
