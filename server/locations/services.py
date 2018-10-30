from locations.models import Location, Place

class LocationService:

    def __init__(self, user):
        self.__user = user

    def get_last_location(self):
        location = Location.objects.filter(user = self.__user).last()
        if location:
            return location
        else:
            return False
    
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
            place_distance = place.distance_from(latitiude, longitude)
            if place_distance < nearest_distance:
                nearest_place = place

        location_type = Place.OTHER
        if nearest_place:
            location_type = nearest_place.type
        return location_type

    def get_location_at(self, datetime):
        pass

    def get_current_timezone(self):
        return "US/Pacific"

    def get_timezone_at(self, datetime):
        pass