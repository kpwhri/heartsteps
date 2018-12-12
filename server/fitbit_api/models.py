import uuid, pytz
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User

class FitbitAccount(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)

    user = models.OneToOneField(User)
    fitbit_user = models.CharField(max_length=32)

    access_token = models.TextField(null=True, blank=True, help_text='The OAuth2 access token')
    refresh_token = models.TextField(null=True, blank=True, help_text='The OAuth2 refresh token')
    expires_at = models.FloatField(null=True, blank=True, help_text='The timestamp when the access token expires')

    def __str__(self):
        return str(self.user)

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

class FitbitActivityType(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    
    fitbit_id = models.IntegerField()
    name = models.CharField(max_length=50)


class FitbitDay(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(FitbitAccount)
    date = models.DateField()
    timezone = models.CharField(max_length=50)

    moderate_minutes = models.FloatField(default=0)
    vigorous_minutes = models.FloatField(default=0)

    step_count = models.FloatField(default=0)

    def get_timezone(self):
        return pytz.timezone(self.timezone)

    def format_date(self):
        return self.date.strftime('%Y-%m-%d')

    def update(self):
        self.update_steps()
        self.update_active_minutes()

    def update_steps(self):
        total_steps = 0
        for step_count in FitbitMinuteStepCount.objects.filter(day=self).all():
            total_steps += step_count.steps
        self.step_count = total_steps
        self.save()

    def update_active_minutes(self):
        moderate_minutes = 0
        vigorous_minutes = 0
        for activity in FitbitActivity.objects.filter(day=self).all():
            moderate_minutes += activity.moderate_minutes
            vigorous_minutes += activity.vigorous_minutes
        self.moderate_minutes = moderate_minutes
        self.vigorous_minutes = vigorous_minutes
        self.save()

    def __str__(self):
        return "%s: %s" % (self.account, self.format_date())

class FitbitActivity(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(FitbitAccount)
    fitbit_id = models.CharField(max_length=50)

    type = models.ForeignKey(FitbitActivityType, null=True, blank=True)
    day = models.ForeignKey(FitbitDay)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    moderate_minutes = models.IntegerField(null=True, blank=True)
    vigorous_minutes = models.IntegerField(null=True, blank=True)

    payload = JSONField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class FitbitMinuteStepCount(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(FitbitAccount)

    day = models.ForeignKey(FitbitDay)
    time = models.DateTimeField()
    steps = models.IntegerField()

class FitbitDailyUnprocessedData(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)

    account = models.ForeignKey(FitbitAccount)
    day = models.OneToOneField(FitbitDay)
    category = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50, null=True, blank=True)

    payload = JSONField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)