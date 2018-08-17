from .models import Location

def get_last_user_location(user):
    location = Location.objects.filter(user=user).last()
    if location:
        return location
    else:
        return False