from django.test import TestCase, override_settings

from django.contrib.auth.models import User
from heartsteps_locations.models import Location, determine_user_location_type

def make_space_needle_location():
    return Location(
        lat = 47.620422,
        long = -122.349358
    )

def make_pie_bar_location():
    return Location(
        lat = 47.6166953,
        long = -122.3273954
    )

def make_kpwri_location():
    return Location(
        lat = 47.6169397,
        long = -122.329572
    )

def make_pedjas_house_location():
    return Location(
        lat = 47.61607,
        long = -122.32676
    )

@override_settings(HEARTSTEPS_LOCATIONS_NEAR_DISTANCE=0.5)
class LocationTests(TestCase):

    def test_distance(self):
        space_needle = make_space_needle_location()
        kpwri = make_kpwri_location()
        pedjas_house = make_pedjas_house_location()

        kpwri_is_near_space_needle = space_needle.is_near(kpwri.lat, kpwri.long)
        self.assertFalse(kpwri_is_near_space_needle)

        pedjas_house_is_near_kpwri = pedjas_house.is_near(kpwri.lat, kpwri.long)
        self.assertTrue(pedjas_house_is_near_kpwri)

    def test_user_at_office(self):
        user = User.objects.create(username="test")

        kpwri = make_kpwri_location()
        kpwri.type = 'office'
        kpwri.user = user
        kpwri.save()

        location = make_pie_bar_location()
        location_type = determine_user_location_type(user, location.lat, location.long)

        self.assertEqual(location_type, 'office')

    def test_user_not_at_office(self):
        user = User.objects.create(username="test")

        kpwri = make_kpwri_location()
        kpwri.type = 'office'
        kpwri.user = user
        kpwri.save()

        location = make_space_needle_location()
        location_type = determine_user_location_type(user, location.lat, location.long)

        self.assertEqual(location_type, 'other') 


    def test_pedja_lives_closer_to_the_pie_bar(self):
        user = User.objects.create(username="pedja")

        kpwri = make_kpwri_location()
        kpwri.type = 'office'
        kpwri.user = user
        kpwri.save()

        home = make_pedjas_house_location()
        home.type = 'home'
        home.user = user
        home.save()

        location = make_pie_bar_location()
        location_type = determine_user_location_type(user, location.lat, location.long)

        self.assertEqual(location_type, 'home')




