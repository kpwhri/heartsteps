from django.db import models
from django.contrib.auth.models import User

INTENSITY = [
    ('m', 'Moderate'),
    ('v', 'Vigorous')
]


class ActivityPlan(models.Model):
    user = models.ForeignKey(User)
    activity_date = models.DateField()
    start_time = models.CharField(max_length=15)
    activity_type = models.CharField(max_length=50)
    intensity = models.CharField(max_length=1, choices=INTENSITY)
    duration = models.IntegerField()
    complete = models.BooleanField(default=False)
    enjoyed = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.complete:
            verb = "completed on"
        else:
            verb = "planned for"
        return "%s %s %s (%s)" % (self.activity_type, verb, self.activity_date, self.user)
