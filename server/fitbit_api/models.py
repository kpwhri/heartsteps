import uuid, pytz, math
from datetime import datetime, timedelta
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User

class FitbitAccount(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    fitbit_user = models.CharField(max_length=32, unique=True)

    access_token = models.TextField(null=True, blank=True, help_text='The OAuth2 access token')
    refresh_token = models.TextField(null=True, blank=True, help_text='The OAuth2 refresh token')
    expires_at = models.FloatField(null=True, blank=True, help_text='The timestamp when the access token expires')

    def __str__(self):
        return str(self.fitbit_user)

    @property
    def authorized(self):
        if None in [self.access_token, self.refresh_token, self.expires_at]:
            return False
        else:
            return True
    
    @property
    def first_updated(self):
        if hasattr(self, '_first_updated'):
            return self._first_updated
        first_update = FitbitSubscriptionUpdate.objects.order_by('created').filter(
            subscription__fitbit_account = self
        ).first()
        if first_update:
            self._first_updated = first_update.created
            return self._first_updated
        else:
            return None

    @property
    def last_updated(self):
        if hasattr(self, '_last_updated'):
            return self._last_updated
        last_update = FitbitSubscriptionUpdate.objects.order_by('created').filter(
            subscription__fitbit_account = self
        ).last()
        if last_update:
            self._last_updated = last_update.created
            return self._last_updated
        else:
            return None

class FitbitAccountUser(models.Model):
    user = models.OneToOneField(User, unique=True)
    account = models.ForeignKey(FitbitAccount)

class FitbitSubscription(models.Model):
    uuid = models.CharField(max_length=50, unique=True, primary_key=True)    
    fitbit_account = models.ForeignKey(FitbitAccount)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.set_uuid()
        super().save(*args, **kwargs)

    def set_uuid(self):
        self.uuid = uuid.uuid4().hex

    def __str__(self):
        return 'Subscription for %s' % (self.fitbit_account)

class FitbitUpdate(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    payload = JSONField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return "Update from FitBit at %s" % (self.created)

class FitbitSubscriptionUpdate(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    update = models.ForeignKey(FitbitUpdate, null=True)
    subscription = models.ForeignKey(FitbitSubscription)
    payload = JSONField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Updated %s at %s' % (str(self.subscription), self.created)
