import uuid
from django.db import models
from django.contrib.auth.models import User

class AuthenticationSession(models.Model):
    token = models.CharField(max_length=50, primary_key=True, unique=True, default=uuid.uuid4)    
    state = models.CharField(max_length=50, null=True, blank=True)
    
    user = models.ForeignKey(User)

    disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class FitbitAccount(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)

    user = models.OneToOneField(User)
    fitbit_user = models.CharField(max_length=32)

    access_token = models.TextField(help_text='The OAuth2 access token')
    refresh_token = models.TextField(help_text='The OAuth2 refresh token')
    expires_at = models.FloatField(help_text='The timestamp when the access token expires')

    def __str__(self):
        return str(self.user)

class FitbitSubscription(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    
    fitbit_account = models.ForeignKey(FitbitAccount)
    active = models.BooleanField(default=False)

    def __str__(self):
        state = 'Inactive'
        if self.active:
            state = 'Active'
        return '%s subscription for %s' % (state, self.fitbit_account)
