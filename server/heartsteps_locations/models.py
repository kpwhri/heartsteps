from django.db import models
from django.conf import settings
from geopy.distance import distance as geopy_distance

from django.contrib.auth.models import User

DISTANCE_RADIUS = settings.HEARTSTEPS_LOCATIONS_NEAR_DISTANCE

HOME = 'home'
OFFICE = 'office'
OTHER = 'other'

LOCATION_TYPES = (
    (HOME, 'Home'),
    (OFFICE, 'Office'),
    (OTHER, 'Other')
)

class Location(models.Model):
    user = models.ForeignKey(User)
    
    address = models.CharField(max_length=250)
    lat = models.FloatField(null=True, blank=True)
    long = models.FloatField(null=True, blank=True)

    type = models.CharField(max_length=10, default=OTHER, choices=LOCATION_TYPES)

    def distance_from(self, lat, lng):
        test_coords = (lat, lng)
        location_coords = (self.lat, self.long)

        distance = geopy_distance(location_coords, test_coords)
        return distance.km

    def is_near(self, lat, lng):
        distance = self.distance_from(lat, lng)
        if distance < DISTANCE_RADIUS:
            return True
        else:
            return False


    def __str__(self):
        return "%s (%s)" % (self.user, self.type)

def determine_user_location_type(user, latitude, longitude):
    near_locations = []
    for location in Location.objects.filter(user=user):
        if location.is_near(latitude, longitude):
            near_locations.append(location)
    
    nearest_location = False
    for location in near_locations:
        if not nearest_location:
            nearest_location = location
            break
        
        nearest_location_distance = nearest_location.distance_from(latitude, longitude)
        location_distance = location.distance_from(latitiude, longitude)
        if location_distance < nearest_location_distance:
            nearest_location = location

    location_type = OTHER
    if nearest_location:
        location_type = nearest_location.type

    return location_type



