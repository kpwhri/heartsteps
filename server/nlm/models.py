from django.db import models

from participants.models import Cohort, Participant


class CohortAssignment(models.Model):
    cohort = models.OneToOneField(Cohort, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

class Level(models.Model):
    """5 Levels: Recovery, Random, N+O, N+R, Full"""
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    
class ParticipantAssignment(models.Model):
    """Contains all NLM Participant"""
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    
    