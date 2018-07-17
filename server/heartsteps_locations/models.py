from django.db import models

from django.contrib.auth.models import User

class Location(models.Model):
    HOME = 'home'
    OFFICE = 'office'
    OTHER = 'other'

    LOCATION_TYPES = (
        (HOME, 'Home'),
        (OFFICE, 'Office'),
        (OTHER, 'Other')
    )

    user = models.ForeignKey(User)
    
    address = models.CharField(max_length=250)
    lat = models.FloatField(null=True, blank=True)
    long = models.FloatField(null=True, blank=True)

    type = models.CharField(max_length=10, default=OTHER, choices=LOCATION_TYPES)

    def __str__(self):
        return "%s (%s)" % (self.user, self.type)

