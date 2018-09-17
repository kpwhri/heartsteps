from rest_framework.test import APITestCase
from django.urls import reverse

from unittest.mock import patch
from rest_framework.response import Response

from django.contrib.auth.models import User

class FitBitAuthorization(APITestCase):

    @patch('fitbit_api.views.redirect')
    @patch('fitbit_api.views.login')
    def test_authorize(self, login, redirect):
        redirect.return_value = Response({})
        user = User.objects.create(username="test")

        response = self.client.get(reverse('fitbit-authorize-login', kwargs={
            'username': 'test'
        }))

        login.assert_called()
        redirect.assert_called()

    def test_process(self):
        response = self.client.get(reverse('fitbit-authorize-process'))

        
