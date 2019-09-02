from datetime import datetime
from datetime import timedelta
import pytz

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Day(models.Model):
    user = models.ForeignKey(
        User,
        related_name="+",
        on_delete = models.CASCADE
    )
    date = models.DateField()
    timezone = models.CharField(max_length=150)

    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        ordering = ['date']
        unique_together = ('user', 'date')

    def get_timezone(self):
        return pytz.timezone(self.timezone)

    def set_start(self):
        self.start = datetime(
            self.date.year,
            self.date.month,
            self.date.day,
            tzinfo = self.get_timezone()
        )

    def set_end(self):
        self.end = datetime(
            self.date.year,
            self.date.month,
            self.date.day,
            tzinfo = self.get_timezone()
        ) + timedelta(days=1)

    def __str__(self):
        return '%s: %s' % (self.user.username, self.date.strftime('%Y-%m-%d'))
