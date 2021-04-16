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
    cohort_assignment = models.ForeignKey(CohortAssignment, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)    

class Conditionality(models.Model):
    """Base Class for all conditionalities"""
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1024)
    module = models.CharField(max_length=1024)
    active = models.BooleanField(default=True)