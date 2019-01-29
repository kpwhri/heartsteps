import uuid, pytz, math
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

class FitbitActivityType(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    
    fitbit_id = models.IntegerField()
    name = models.CharField(max_length=50)


class FitbitDay(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(FitbitAccount)
    date = models.DateField()
    timezone = models.CharField(max_length=50, default=pytz.UTC.zone)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]

    @property
    def step_count(self):
        total_steps = 0
        for step_count in FitbitMinuteStepCount.objects.filter(day=self).all():
            total_steps += step_count.steps
        return total_steps

    def get_timezone(self):
        return pytz.timezone(self.timezone)

    def format_date(self):
        return self.date.strftime('%Y-%m-%d')

    def update(self):
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

    average_heart_rate = models.IntegerField(null=True)

    payload = JSONField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def id(self):
        return str(self.uuid)

    @property
    def duration(self):
        difference = self.end_time - self.start_time
        return math.ceil(difference.seconds/60)

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
