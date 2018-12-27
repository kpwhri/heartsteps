import uuid

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Week(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(User)

    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def id(self):
        return str(self.uuid)

    def __str__(self):
        return "%s to %s (%s)" % (self.start_date, self.end_date, self.user)
