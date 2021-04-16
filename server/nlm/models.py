from django.db import models

from django.contrib.auth.models import User
from participants.models import Cohort, Participant


class CohortAssignment(models.Model):
    cohort = models.OneToOneField(Cohort, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

class Level(models.Model):
    """5 Levels: Recovery, Random, N+O, N+R, Full"""
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    
class ParticipantAssignment(models.Model):  # roster for NLM study
    """Contains all NLM Participant"""
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    # it should be changed to OneToManyField if we extend study type
    cohort_assignment = models.ForeignKey(CohortAssignment, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)    

class Conditionality(models.Model):
    """Base Class for all conditionalities"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=1024)
    module = models.CharField(max_length=1024, unique=True)
    """each module has only one conditionality object"""
    active = models.BooleanField(default=True)
    """means whether the conditionality is running or not. This can be reset to True anytime."""
    class Meta:
        unique_together = ['name', 'user']