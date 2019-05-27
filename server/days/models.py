from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Day(models.Model):
    user = models.ForeignKey(User, related_name="days")
    date = models.DateField()
    timezone = models.CharField(max_length=150)

    def __str__(self):
        return '%s: %s' % (self.user.username, self.date.strftime('%Y-%m-%d'))
