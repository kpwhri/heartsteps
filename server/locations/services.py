import pytz
from datetime import datetime, date

from django.utils import timezone

from timezonefinder import TimezoneFinder

from locations.models import Location, Place, User
from locations.serializers import LocationSerializer
from locations.signals import timezone_updated

class LocationService:

    class UnknownLocation(Exception):
        pass

    class InvalidLocation(Exception):
        pass

    def __init__(self, user):
        self.__user = user

    def update_location(self, location_object):
        serialized_location = LocationSerializer(data=location_object)
        if serialized_location.is_valid():
            location = Location(**serialized_location.validated_data)
            location.user = self.__user
            location.time = timezone.now()
            location.save()
            return location
        else:
            raise self.InvalidLocation()

    def get_last_location(self):
        location = Location.objects.filter(user = self.__user).first()
        if not location:
            raise self.UnknownLocation()
        return location
    
    def categorize_location(self, latitude, longitude):
        near_by_places = []
        for place in Place.objects.filter(user=self.__user):
            if place.is_near(latitude, longitude):
                near_by_places.append(place)
        nearest_place = False
        for place in near_by_places:
            if not nearest_place:
                nearest_place = place
                break
            nearest_distance = nearest_place.distance_from(latitude, longitude)
            place_distance = place.distance_from(latitude, longitude)
            if place_distance < nearest_distance:
                nearest_place = place

        location_type = Place.OTHER
        if nearest_place:
            location_type = nearest_place.type
        return location_type

    def get_location_on(self, time):
        if type(time) is date:
            time = datetime(time.year, time.month, time.day, 23, 59)
        if not time.tzinfo:
            time = pytz.UTC.localize(time)
        location = Location.objects.filter(time__lte=time).first()
        if not location:
            raise self.UnknownLocation()
        return location

    def get_current_timezone(self):
        return self.get_timezone_on(timezone.now())

    def get_current_datetime(self):
        tz = self.get_current_timezone()
        return timezone.now().astimezone(tz)

    def get_timezone_for(self, latitude, longitude):
        timezone_finder = TimezoneFinder()
        timezone = timezone_finder.timezone_at(
            lng = longitude,
            lat = latitude
        )
        return pytz.timezone(timezone)

    def get_timezone_on(self, datetime):
        try:
            location = self.get_location_on(datetime)
            return self.get_timezone_for(
                latitude = location.latitude,
                longitude = location.longitude
            )
        except LocationService.UnknownLocation:
            return pytz.UTC 

    def check_timezone_change(self):
        locations = Location.objects.filter(user=self.__user)[:2]

        if not len(locations):
            pass
        elif len(locations) < 2:
            timezone_updated.send(User, username=self.__user.username)
        else:
            new_timezone = self.get_timezone_for(
                latitude = locations[0].latitude,
                longitude = locations[0].longitude
            )
            current_timezone = self.get_timezone_for(
                latitude = locations[1].latitude,
                longitude = locations[1].longitude
            )

            if current_timezone is not new_timezone:
                timezone_updated.send(User, username=self.__user.username)
