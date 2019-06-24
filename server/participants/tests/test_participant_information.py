from unittest.mock import patch
import datetime

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

from participants.models import Participant
from participants.models import User

class ParticipantInformationViewTests(APITestCase):

    def test_401_if_not_authenticated(self):
        response = self.client.get(reverse('participants-information'))

        self.assertEqual(response.status_code, 401)

    def test_404_if_no_participant(self):
        user = User.objects.create(username='test')

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('participants-information'))

        self.assertEqual(response.status_code, 404)
        
    def test_returns_heartsteps_id(self):
        user = User.objects.create(username='test')
        Participant.objects.create(
            user = user,
            heartsteps_id = 'sample-id',
            enrollment_token = 'token'
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('participants-information'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['heartstepsId'], 'sample-id')
        self.assertEqual(response.data['staff'], False)
        self.assertEqual(response.data['date_enrolled'], datetime.date.today().strftime('%Y-%m-%d'))

    def test_returns_staff_status(self):
        user = User.objects.create(
            username='test',
            is_staff=True
        )
        Participant.objects.create(
            user = user,
            heartsteps_id = 'sample-id',
            enrollment_token = 'token'
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('participants-information'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['staff'], True)

