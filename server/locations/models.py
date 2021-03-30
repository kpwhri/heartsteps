from django.db import models
from django.conf import settings
from geopy.distance import distance as geopy_distance
import pytz
from timezonefinder import TimezoneFinder

from django.contrib.auth.models import User

DISTANCE_RADIUS = settings.HEARTSTEPS_LOCATIONS_NEAR_DISTANCE

class Place(models.Model):
    HOME = 'home'
    WORK = 'work'
    OTHER = 'other'

    CATEGORIES = (
        (HOME, 'Home'),
        (WORK, 'work'),
        (OTHER, 'Other')
    )

    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE
        )
    
    address = models.CharField(max_length=250, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    type = models.CharField(max_length=10, default=OTHER, choices=CATEGORIES)

    def distance_from(self, latitude, longitude):
        test_coords = (latitude, longitude)
        location_coords = (self.latitude, self.longitude)

        distance = geopy_distance(location_coords, test_coords)
        return distance.km

    def is_near(self, latitude, longitude):
        distance = self.distance_from(latitude, longitude)
        if distance < DISTANCE_RADIUS:
            return True
        else:
            return False


    def __str__(self):
        return "%s (%s)" % (self.user, self.type)

class Location(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE
        )
    latitude = models.FloatField()
    longitude = models.FloatField()

    time = models.DateTimeField()

    source = models.CharField(max_length=50, null=True)

    category = models.CharField(
        max_length = 20,
        choices = Place.CATEGORIES,
        null = True
    )

    class Meta:
        ordering = ['-time', 'user']

    def __str__(self):
        return "%s @ %s" % (self.user, self.time)

    def calculate_timezone(self):
        timezone_finder = TimezoneFinder()
        timezone = timezone_finder.timezone_at(
            lng = self.longitude,
            lat = self.latitude
        )
        if timezone:
            return pytz.timezone(timezone)
        else:
            return pytz.UTC

    @property
    def timezone(self):
        return self.calculate_timezone()
    
    @property
    def local_time(self):
        return self.time.astimezone(self.timezone)
