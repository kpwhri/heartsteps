from locations.models import Location, Place, OTHER

def get_last_user_location(user):
    location = Location.objects.filter(user=user).last()
    if location:
        return location
    else:
        return False

def determine_location_type(user, latitude, longitude):
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