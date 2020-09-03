import pytz
from datetime import datetime, date, timedelta

from django.utils import timezone

from timezonefinder import TimezoneFinder

from locations.models import Location, Place, User
from locations.serializers import LocationSerializer

class LocationService:

    class UnknownLocation(Exception):
        pass

    class InvalidLocation(Exception):
        pass

    def __init__(self, user=None, username=None):
        if username:
            user = User.objects.get(username=username)
        if not user:
            raise RuntimeException('No user specified')
        self.__user = user

    def update_location(self, location_object):
        serialized_location = LocationSerializer(data=location_object)
        if serialized_location.is_valid():
            location = Location(**serialized_location.validated_data)
            location.user = self.__user
            location.time = timezone.now()
            location.category = self.categorize_location(
                latitude = location.latitude,
                longitude = location.longitude
            )
            location.save()
            return location
        else:
            raise self.InvalidLocation()
    
    def get_current_location(self):
        return self.get_last_location()

    def get_last_location(self):
        location = Location.objects.filter(user = self.__user).first()
        if location:
            return location
        else:
            raise self.UnknownLocation()

    def get_recent_location(self):
        return self.get_location_near(timezone.now())

    def get_location_near(self, time):
        location = Location.objects.filter(
            user = self.__user,
            time__lte = time,
            time__gte = time - timedelta(minutes=60)
        ).first()
        if location:
            return location
        else:
            raise self.UnknownLocation()
    def get_places(self):
        if not hasattr(self, '_places'):
            self._places = Place.objects.filter(
                user = self.__user
            ).all()
        return self._places
    
    def categorize_location(self, latitude, longitude):
        near_by_places = []
        for place in self.get_places():
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
        location = Location.objects.filter(
            user=self.__user,
            time__lte=time
        ).first()
        if not location:
            raise LocationService.UnknownLocation()
        return location

    def get_current_timezone(self):
        return self.get_timezone_on(timezone.now())

    def get_current_datetime(self):
        tz = self.get_current_timezone()
        return timezone.now().astimezone(tz)
    
    def get_current_date(self):
        current_datetime = self.get_current_datetime()
        return date(current_datetime.year, current_datetime.month, current_datetime.day)

    def get_timezone_for(self, latitude, longitude):
        return LocationService.get_timezone_at(latitude, longitude)

    def get_timezone_at(latitude, longitude):
        timezone_finder = TimezoneFinder()
        timezone = timezone_finder.timezone_at(
            lng = longitude,
            lat = latitude
        )
        if timezone:
            return pytz.timezone(timezone)
        else:
            return pytz.UTC

    def get_timezone_on(self, datetime):
        try:
            location = self.get_location_on(datetime)
            return self.get_timezone_for(
                latitude = location.latitude,
                longitude = location.longitude
            )
        except LocationService.UnknownLocation:
            return pytz.UTC

    def get_datetime_on(self, datetime):
        timezone = self.get_timezone_on(datetime)
        return datetime.astimezone(timezone)

    def get_home_location(self):
        home = Place.objects.filter(
            user = self.__user,
            type = Place.HOME
        ).first()
        if home:
            location = Location(
                user = self.__user,
                latitude = home.latitude,
                longitude = home.longitude
            )
            return location
        else:
            raise LocationService.UnknownLocation('No home location set')

    def get_default_location(self):
        return self.get_home_location()

    def get_home_timezone(self):
        try:
            home = self.get_home_location()
            return self.get_timezone_for(
                latitude = home.latitude,
                longitude = home.longitude
            )
        except LocationService.UnknownLocation:
            return pytz.UTC

    def get_home_current_datetime(self):
        tz = self.get_home_timezone()
        return timezone.now().astimezone(tz)

    def get_home_current_date(self):
        dt = self.get_home_current_datetime()
        return date(
            dt.year,
            dt.month,
            dt.day
        )
