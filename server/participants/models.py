from django.db import models
from django.contrib.auth.models import User

from fcm_django.models import FCMDevice

class Participant(models.Model):
    """
    Represents a study participant

    When the participant is enrolled, a user is created.
    """
    heartsteps_id = models.CharField(primary_key=True, max_length=25)
    enrollment_token = models.CharField(max_length=10)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
            if self.user:
                return "%s (enrolled)" % (self.heartsteps_id)
            return self.heartsteps_id