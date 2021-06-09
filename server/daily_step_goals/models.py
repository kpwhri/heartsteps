from django.db import models

# Create your models here.
class StepGoals(models.Model):
    date = models.DateField()
    step_goal = models.Integer
