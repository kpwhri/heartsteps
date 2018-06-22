from django.db import models
from django.contrib.auth.models import User

# Open questions:
# Should User be a FK for all Fitbit models?  Participant?


class WeatherForecast(models.Model):
    """
    Represents an hourly weather forecast
    currently using the DarkSky API
    """
    user = models.ForeignKey(User)
    latitude = models.FloatField()
    longitude = models.FloatField()
    time = models.DateTimeField()
    precip_probability = models.FloatField()
    precip_type = models.StringField(max_length=32)
    temperature = models.FloatField()
    apparent_temperature = models.FloatField()
    wind_speed = models.FloatField()
    cloud_cover = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tracker(models.Model):
    """
    Tracker Get Device API (e.g, specific Fitbit)
    https://dev.fitbit.com/build/reference/web-api/devices/
    """
    user = models.ForeignKey(User)
    # Device type can be TRACKER, SCALE, maybe other non-fitbits
    device_type = models.CharField(max_length=20)
    # Battery can be empty, high
    battery = models.CharField(max_length=20)
    # Device subtype (Charge HR, Alta, Aria)
    device_version = models.CharField(max_length=20)
    last_sync_dtm = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerOAuth(models.Model):
    """
    Fitbit OAuth credentials required to access records
    https://dev.fitbit.com/build/reference/web-api/oauth2/
    """
    tracker = models.ForeignKey(Tracker)
    # Actual token for access
    access_token = models.CharField(max_length=64)
    # Token to retrieve access token
    refresh_token = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerActivitySteps(models.Model):
    """
    Fitbit Get Activity Time Series API (/steps)
    https://dev.fitbit.com/build/reference/web-api/activity/
    Could also track minutes of activity by intensity, distance,
    duration
    """
    tracker = models.ForeignKey(Tracker)
    # Fitbit returns date & time as separate fields
    tracker_dt = models.DateField()
    tracker_tm = models.TimeField()
    # Timezone. Will require a call to device to obtain
    tracker_tz = models.CharField(max_length=48)
    steps = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerActivityCalories(models.Model):
    """
    Fitbit Get Activity Time Series API (/calories)
    """
    tracker = models.ForeignKey(Tracker)
    tracker_dt = models.DateField()
    tracker_tm = models.TimeField()
    tracker_tz = models.CharField(max_length=48)
    calories = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerBodyWeight(models.Model):
    """
    Fitbit Get Weight Logs API
    https://dev.fitbit.com/build/reference/web-api/body/
    """
    tracker = models.ForeignKey(Tracker)
    tracker_dt = models.DateField()
    tracker_tm = models.TimeField()
    tracker_tz = models.CharField(max_length=48)
    # How data was input: API, Aria
    source = models.CharField(max_length=24)
    bmi = models.FloatField()
    weight = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerHeartRate(models.Model):
    """
    Fitbit Get Heart Rate Time Series API
    https://dev.fitbit.com/build/reference/web-api/heart-rate/
    """
    tracker = models.ForeignKey(Tracker)
    tracker_dt = models.DateField()
    tracker_tm = models.TimeField()
    tracker_tz = models.CharField(max_length=48)
    heartrate = models.IntegerField
    # Number of unit in dataset_type
    dataset_interval = models.FloatField()
    # Unit for dataset_interval (should be 'second' for intraday)
    dataset_type = models.CharField(max_length=24)
    weight = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerSleep(models.Model):
    """
    Fitbit Get Sleep Logs by Date API
    https://dev.fitbit.com/build/reference/web-api/sleep/
    """
    tracker = models.ForeignKey(Tracker)
    tracker_dt = models.DateField()
    total_minutes_asleep = IntegerField()
    total_sleep_records = IntegerField()
    total_time_in_bed = IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
