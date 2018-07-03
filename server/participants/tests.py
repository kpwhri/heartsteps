from django.urls import reverse

from .models import Participant
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

class EnrollViewTests(APITestCase):
    def test_enrollment_token(self):
        """
        Returns an auth token when valid 
        enrollment token is passed
        """
        Participant.objects.create(
            user = User.objects.create(username='test'),
            id = 123,
            enrollment_token = 'token'
        )

        response = self.client.post(reverse('participants-enroll'), {
            'enrollment_token': 'token'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['token'])
        self.assertEqual(response.data['participant_id'], 123)

    def test_no_matching_enrollment_token(self):
        """
        If the enrollment token doesn't match an object in the database
        the response returns an error
        """
        response = self.client.post(reverse('participants-enroll'), {
            'enrollment_token': 'doesnt-exist'
        })

        self.assertEqual(response.status_code, 400)

    def test_no_enrollment_token(self):
        response = self.client.post(reverse('participants-enroll'), {

        })

        self.assertEqual(response.status_code, 400)

class DeviceRegistration(APITestCase):

    def test_save_token(self):
        participant = Participant.objects.create(
            user = User.objects.create(username='test'),
            id = 123,
            enrollment_token = 'token'
        )

        self.client.force_authenticate(participant.user)

        response = self.client.post(reverse('participants-device'), {
            'registration': 'sample-token',
            'device_type': 'web'
        })

        self.assertEqual(response.status_code, 200)
