from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from rest_framework.test import APITestCase
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from .models import ClockFacePin

class ClockFacePinAuthorizationTest(APITestCase):
    def test_everything(self):
        # watch gets pin
        response = self.client.post(reverse('pin-gen-myarr'))
        self.assertEquals(response.status_code, 200)

        self.pin = response.json()['pin']
        self.uniid = response.json()['uniid']

        # check for pair (phone-to-server)
        user = User.objects.create(username="test01")
        tk = Token.objects.create(user=user)
       
        self.client.force_authenticate(user)
        response = self.client.post(reverse('pin-gen-pair'), {
            'pin': self.pin
        })
        self.assertEquals(response.status_code, 200)

        # check for user (watch-to-server)
        response = self.client.post(reverse('pin-gen-user'), {
            'pin': self.pin,
            'uniid': self.uniid
        })
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['authenticated'], True)

    def test_pair_get(self):
        user = User.objects.create(username="test01")
        self.client.force_authenticate(user)

        response = self.client.get(reverse("pin-gen-pair"))
        self.assertEquals(response.status_code, 404)

    def test_pair_post(self):
        user = User.objects.create(username="test01")       
        self.client.force_authenticate(user)

        response = self.client.post(reverse("pin-gen-pair"), {
            'pin': "01234"
        })
        self.assertEquals(response.status_code, 400)





        








