import uuid, pytz, math
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User

class FitbitAccountQuerySet(models.QuerySet):

    _load_summary = False
    _summary_loaded = False

    def _clone(self, *args, **kwargs):
        clone = super()._clone(*args, **kwargs)
        clone._load_summary = self._load_summary
        clone._summary_loaded = self._summary_loaded
        return clone

    def prefetch_summary(self):
        self._load_summary = True
        return self

    def _fetch_all(self):
        super()._fetch_all()
        if self._result_cache and self._load_summary and not self._summary_loaded:
            self.load_summaries()
            self._summary_loaded = True

    def load_summaries(self):
        summaries = FitbitAccountSummary.objects.filter(
            account__in = [account for account in self._result_cache] 
        ) \
        .prefetch_related('first_update') \
        .prefetch_related('last_update') \
        .all()
        summary_by_account_id = {}
        for summary in summaries:
            summary_by_account_id[summary.account_id] = summary
        for account in self._result_cache:
            if account.uuid in summary_by_account_id:
                account._fitbit_account_summary = summary_by_account_id[account.uuid]
            else:
                account._fitbit_account_summary = None

class FitbitAccount(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    fitbit_user = models.CharField(max_length=32, unique=True)

    access_token = models.TextField(null=True, blank=True, help_text='The OAuth2 access token')
    refresh_token = models.TextField(null=True, blank=True, help_text='The OAuth2 refresh token')
    expires_at = models.FloatField(null=True, blank=True, help_text='The timestamp when the access token expires')

    objects = FitbitAccountQuerySet.as_manager()

    def __str__(self):
        return str(self.fitbit_user)

    @property
    def authorized(self):
        if None in [self.access_token, self.refresh_token, self.expires_at]:
            return False
        else:
            return True

    @property
    def fitbit_account_summary(self):
        if not hasattr(self, '_fitbit_account_summary'):
            self._fitbit_account_summary = self.get_fitbit_account_summary()
        return self._fitbit_account_summary

    def get_fitbit_account_summary(self):
        try:
            return FitbitAccountSummary.objects.get(account = self)
        except FitbitAccountSummary.DoesNotExist:
            return FitbitAccountSummary.objects.create(
                account = self,
                first_update = FitbitAccountUpdate.objects.filter(account=self).first(),
                last_update = FitbitAccountUpdate.objects.filter(account=self).last(),
            )
    
    @property
    def first_updated(self):
        if not hasattr(self, '_first_updated'):
            first_update = self.get_first_update()      
            if first_update:
                self._first_updated = first_update.created
            else:
                self._first_updated = None
        return self._first_updated

    def get_first_update(self):
        return self.fitbit_account_summary.first_update

    @property
    def last_updated(self):
        if not hasattr(self, '_last_updated'):
            last_update = self.get_last_update()
            if last_update:
                self._last_updated = last_update.created
            else:
                self._last_updated = None
        return self._last_updated

    def get_last_update(self):
        return self.fitbit_account_summary.last_update

    def was_updated_between(self, start, end):
        subscription_updates = FitbitSubscriptionUpdate.objects.filter(
            subscription__fitbit_account = self,
            created__gte = start,
            created__lte = end
        ).count()
        account_updates = FitbitAccountUpdate.objects.filter(
            account = self,
            created__gte = start,
            created__lte = end
        ).count()
        if subscription_updates > 0 or account_updates > 0:
            return True
        else:
            return False

    @property
    def last_device_update(self):
        if hasattr(self, '_last_device_update'):
            return self._last_device_update
        self._last_device_update = self.get_last_tracker_sync_time()
        return self._last_device_update

    def get_last_tracker_sync_time(self):
        last_update = FitbitDeviceUpdate.objects\
            .filter(fitbit_device__account=self)\
            .order_by('time')\
            .last()
        if last_update:
            return last_update.time
        else:
            return None

    def get_users(self):
        account_users = FitbitAccountUser.objects.filter(
            account = self
        ) \
        .prefetch_related('user') \
        .all()
        return [au.user for au in account_users]
    
    def remove_credentials(self):
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.save()

class FitbitAccountUser(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, unique=True)
    account = models.ForeignKey(FitbitAccount, on_delete = models.CASCADE)

class FitbitSubscription(models.Model):
    uuid = models.CharField(max_length=50, unique=True, primary_key=True)    
    fitbit_account = models.ForeignKey(FitbitAccount, on_delete = models.CASCADE)

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
    payload = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return "Update from FitBit at %s" % (self.created)

class FitbitAccountUpdate(models.Model):
    account = models.ForeignKey(
        FitbitAccount,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    update = models.ForeignKey(
        FitbitUpdate,
        null=True,
        on_delete = models.SET_NULL
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            summary = FitbitAccountSummary.objects.get(account_id = self.account_id)
            summary.last_update = self
            summary.save()
        except FitbitAccountSummary.DoesNotExist:
            FitbitAccountSummary.objects.create(
                account_id = self.account_id,
                last_update = self
            )

    def __str__(self):
        return 'Fitbit account %s updated at %s' % (self.account.fitbit_user, self.created)

class FitbitSubscriptionUpdate(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    update = models.ForeignKey(FitbitUpdate, null=True, on_delete = models.CASCADE)
    subscription = models.ForeignKey(FitbitSubscription, on_delete = models.CASCADE)
    payload = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Updated %s at %s' % (str(self.subscription), self.created)


class FitbitDevice(models.Model):

    TRACKER = 'TRACKER'

    account = models.ForeignKey(
        FitbitAccount,
        on_delete = models.CASCADE,
        related_name = '+'
        )
    fitbit_id = models.CharField(max_length=125)
    mac = models.CharField(max_length=125, null=True)
    device_type = models.CharField(max_length=125, null=True)
    device_version = models.CharField(max_length=125, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def add_update(self, time, battery_level):
        FitbitDeviceUpdate.objects.update_or_create(
            fitbit_device = self,
            time = time,
            defaults = {
                'battery_level': battery_level
            }
        )

    @property
    def last_updated(self):
        update = FitbitDeviceUpdate.objects.filter(fitbit_device=self).order_by('time').last()
        return update.time

class FitbitDeviceUpdate(models.Model):
    fitbit_device = models.ForeignKey(FitbitDevice, on_delete = models.CASCADE)
    
    time = models.DateTimeField()
    battery_level = models.IntegerField(null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class FitbitAccountSummary(models.Model):
    account = models.ForeignKey(
        FitbitAccount,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    first_update = models.ForeignKey(
        FitbitAccountUpdate,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )
    last_update = models.ForeignKey(
        FitbitAccountUpdate,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )
