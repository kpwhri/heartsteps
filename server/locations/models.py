from django.db import models
from django.conf import settings
from geopy.distance import distance as geopy_distance

from django.contrib.auth.models import User

DISTANCE_RADIUS = settings.HEARTSTEPS_LOCATIONS_NEAR_DISTANCE

HOME = 'home'
OFFICE = 'office'
OTHER = 'other'

PLACE_TYPES = (
    (HOME, 'Home'),
    (OFFICE, 'Office'),
    (OTHER, 'Other')
)

class Location(models.Model):
    user = models.ForeignKey(User)
    latitude = models.FloatField()
    longitude = models.FloatField()

    time = models.DateTimeField()

    def __str__(self):
        return "%s @ %s" % (self.user, self.time)

class Place(models.Model):
    user = models.ForeignKey(User)
    
    address = models.CharField(max_length=250, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    type = models.CharField(max_length=10, default=OTHER, choices=PLACE_TYPES)

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

def determine_place_type(user, latitude, longitude):
    places = []
    for place in Place.objects.filter(user=user):
        if place.is_near(latitude, longitude):
            places.append(place)
    
    nearest_place = False
    for place in places:
        if not nearest_place:
            nearest_place = place
            break
        
        nearest_distance = nearest_place.distance_from(latitude, longitude)
        place_distance = place.distance_from(latitiude, longitude)
        if place_distance < nearest_distance:
            nearest_place = place

    location_type = OTHER
    if nearest_place:
        location_type = nearest_place.type

    return location_type

def get_last_user_location(user):
    return Location.objects.filter(user=user).last()
