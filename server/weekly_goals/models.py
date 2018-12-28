from django.db import models

from weeks.models import Week, User

class WeeklyGoal(models.Model):

    user = models.ForeignKey(User)
    week = models.OneToOneField(Week)

    minutes = models.IntegerField()
    confidence = models.FloatField()
