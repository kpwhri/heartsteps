from django.db import models

from django.contrib.auth.models import User
from participants.models import Cohort, Participant

class StudyType(models.Model):
    name = models.CharField(max_length=255)
    admins = models.ManyToManyField(User, blank=False)
    active = models.BooleanField(default=True)

class CohortAssignment(models.Model):
    cohort = models.OneToOneField(Cohort, on_delete=models.CASCADE)
    studytype = models.ForeignKey(StudyType, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

class Level(models.Model):
    """5 Levels: Recovery, Random, N+O, N+R, Full"""
    name = models.CharField(max_length=100)
    studytype = models.ForeignKey(StudyType, on_delete=models.CASCADE)
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
    description = models.TextField(max_length=1024)
    studytype = models.ForeignKey(StudyType, on_delete=models.CASCADE)
    module_path = models.CharField(max_length=1024, unique=True)
    """each module has only one conditionality object"""
    active = models.BooleanField(default=True)
    """means whether the conditionality is running or not. This can be reset to True anytime."""
    class Meta:
        unique_together = ['name', 'studytype']


class LogSubject(models.Model):
    name = models.CharField(max_length=255)

class LogObject(models.Model):
    name = models.CharField(max_length=255)

class LogPurpose(models.Model):
    name = models.CharField(max_length=255)

class LogContents(models.Model):
    logtime = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(LogSubject, on_delete=models.CASCADE)
    object = models.ForeignKey(LogObject, on_delete=models.CASCADE)
    purpose = models.ForeignKey(LogPurpose, on_delete=models.DO_NOTHING)
    value = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['-logtime']),
            models.Index(fields=['subject', 'object', 'purpose']),  # also covers s+o, s
            models.Index(fields=['subject', 'purpose']),            
            models.Index(fields=['purpose', 'object']),             # also covers p
            models.Index(fields=['object'])
        ]

class ConditionalityParameter(models.Model):
    conditionality = models.ForeignKey(Conditionality, null=True, on_delete=models.SET_NULL)
    participant = models.ForeignKey(Participant, null=True, on_delete=models.SET_NULL)
    parameter_fullname = models.CharField(max_length=1024)
    period_begin = models.DateTimeField(auto_now_add=True)
    period_finish = models.DateTimeField(null=True)
    value = models.CharField(max_length=255)
    value_type = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ['conditionality', 'participant', 'parameter_fullname', 'period_begin', 'period_finish']
    