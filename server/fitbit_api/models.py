import uuid
from django.db import models
from django.contrib.auth.models import User

from fitapp.models import UserFitbit

class FitbitAccount(UserFitbit):
    class Meta:
        app_label = 'fitbit_api'

class FitbitSubscription(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    
    fitbit_account = models.ForeignKey(FitbitAccount)
    active = models.BooleanField(default=False)

    def __str__(self):
        state = 'Inactive'
        if self.active:
            state = 'Active'
        return '%s subscription for %s' % (state, self.fitbit_account)
