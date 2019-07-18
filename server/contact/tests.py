from rest_framework.test import APITestCase
from django.urls import reverse

from django.contrib.auth.models import User
from .models import ContactInformation

class ContactViewTests(APITestCase):

    def test_get_contact_information(self):
        user = User.objects.create(username="test")

        ContactInformation.objects.create(
            user = user,
            name = "Test User",
            email = "test@user.com",
            phone = "1234567890"
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('contact-information'))

        self.assertEqual(response.status_code, 200)

    def test_get_contact_with_no_information(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('contact-information'))

        self.assertEqual(response.status_code, 404)

    def test_update_contact_information(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('contact-information'), {
            'name':'Sample User Name',
            'email':'example@user.com',
            'phone':"1234567890"
        })
        
        self.assertEqual(response.status_code, 200)