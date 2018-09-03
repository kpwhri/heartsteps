from django.db import models
from django.contrib.auth.models import User

DAYS_OF_WEEK = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday')
]

class ReflectionTime(models.Model):
    user = models.ForeignKey(User)

    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)
    time = models.CharField(max_length=15)

    active = models.BooleanField(default=True)

    def __str__(self):
        if self.active:
            return "%s at %s (%s)" % (self.day, self.time, self.user)
        else:
            return "Inactive (%s)" % (self.user)

class Week(models.Model):
    user = models.ForeignKey(User)
    
    start_date = models.DateField()
    end_date = models.DateField()

    reflection_time = models.ForeignKey(ReflectionTime)

    def __str__(self):
        return "%s to %s (%s)" % (self.start_date, self.end_date, self.user)
