from django.db import models

from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

from activity_summaries.models import Day

# Create your models here.
class StepGoals(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    date = models.DateField()
    step_goal = models.PositiveIntegerField()

    @property
    def id(self):
        return str(self.uuid)

# class Steps(Day):
#     date = models.DateField()
#     steps = models.PositiveIntegerField(default=0)
