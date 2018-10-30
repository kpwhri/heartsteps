import pytz

from timezonefinder import TimezoneFinder

from locations.models import Location, Place

class LocationService:

    class UnknownLocation(Exception):
        pass

    def __init__(self, user):
        self.__user = user

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

    def get_location_on(self, datetime):
        location = Location.objects.filter(time__lte=datetime).first()
        if not location:
            raise self.UnknownLocation()
        return location

    def get_current_timezone(self):
        location = self.get_last_location()
        return self.get_timezone_for(
            latitude = location.latitude,
            longitude = location.longitude
        )

    def get_timezone_for(self, latitude, longitude):
        timezone_finder = TimezoneFinder()
        timezone = timezone_finder.timezone_at(
            lng = longitude,
            lat = latitude
        )
        return pytz.timezone(timezone)

    def get_timezone_on(self, datetime):
        location = self.get_location_on(datetime)
        return self.get_timezone_for(
            latitude = location.latitude,
            longitude = location.longitude
        )