import json

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, override_settings

from rest_framework.test import APITestCase

from locations.models import Place, Location
from locations.services import LocationService

def make_space_needle_location():
    return Place(
        latitude = 47.620422,
        longitude = -122.349358
    )

def make_pie_bar_location():
    return Place(
        latitude = 47.6166953,
        longitude = -122.3273954
    )

def make_kpwri_location():
    return Place(
        latitude = 47.6169397,
        longitude = -122.329572
    )

def make_pedjas_house_location():
    return Place(
        latitude = 47.61607,
        longitude = -122.32676
    )

@override_settings(HEARTSTEPS_LOCATIONS_NEAR_DISTANCE=0.5)
class PlaceTests(TestCase):

    def test_distance(self):
        space_needle = make_space_needle_location()
        kpwri = make_kpwri_location()
        pedjas_house = make_pedjas_house_location()

        kpwri_is_near_space_needle = space_needle.is_near(kpwri.latitude, kpwri.longitude)
        self.assertFalse(kpwri_is_near_space_needle)

        pedjas_house_is_near_kpwri = pedjas_house.is_near(kpwri.latitude, kpwri.longitude)
        self.assertTrue(pedjas_house_is_near_kpwri)

    def test_user_at_office(self):
        user = User.objects.create(username="test")

        kpwri = make_kpwri_location()
        kpwri.type = 'office'
        kpwri.user = user
        kpwri.save()

        place = make_pie_bar_location()

        location_service = LocationService(user)
        place_type = location_service.categorize_location(place.latitude, place.longitude)

        self.assertEqual(place_type, 'office')

    def test_user_not_at_office(self):
        user = User.objects.create(username="test")

        kpwri = make_kpwri_location()
        kpwri.type = 'office'
        kpwri.user = user
        kpwri.save()

        place = make_space_needle_location()

        location_service = LocationService(user)
        place_type = location_service.categorize_location(place.latitude, place.longitude)

        self.assertEqual(place_type, 'other') 

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

        place = make_pie_bar_location()

        location_service = LocationService(user)
        place_type = location_service.categorize_location(place.latitude, place.longitude)

        self.assertEqual(place_type, 'home')

class PlacesViewTests(APITestCase):

    def setup_user(self):
        user = User.objects.create(username="test")
        
        kpwri = make_kpwri_location()
        kpwri.type = 'office'
        kpwri.user = user
        kpwri.save()

        home = make_pedjas_house_location()
        home.type = 'home'
        home.user = user
        home.save()

        return user

    def test_get_user_places(self):
        user = self.setup_user()

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('locations-places'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_update_user_places(self):
        user = self.setup_user()

        self.assertEqual(Place.objects.filter(user=user).count(), 2)

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('locations-places'), json.dumps([{
                'type': 'home',
                'latitude': 17.9,
                'longitude': 15.5
            }]),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Place.objects.filter(user=user).count(), 1)

class LocationsUpdateViewTests(APITestCase):

    def test_update_location(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('locations-update'), {
            'latitude': 123.123,
            'longitude': 123.123,
            'source': 'test source'
        })

        self.assertEqual(response.status_code, 201)

        location = Location.objects.get(user=user)
        self.assertEqual(location.latitude, float(123.123))