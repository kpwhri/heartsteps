from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

from activity_suggestions.models import Configuration as ActivitySuggestionConfiguration

from .models import Participant

class EnrollViewTests(APITestCase):
    def test_enrollment_token(self):
        """
        Returns an authorization token and participant's heartsteps_id when a
        valid enrollment token is passed
        """
        Participant.objects.create(
            user = User.objects.create(username="test"),
            heartsteps_id = "sample-id",
            enrollment_token = 'token'
        )

        response = self.client.post(reverse('participants-enroll'), {
            'enrollmentToken': 'TOKEN'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response['Authorization-Token'])
        self.assertEqual(response.data['heartstepsId'], "sample-id")


    def test_enrollment_create_user(self):
        """
        Creates and authenticates a user if the participant doesn't have a user
        """
        Participant.objects.create(
            heartsteps_id = "sample-id",
            enrollment_token="token"
        )

        response = self.client.post(reverse('participants-enroll'), {
            'enrollmentToken': 'token'
        })

        self.assertEqual(response.status_code, 200)

        participant = Participant.objects.get(heartsteps_id = "sample-id")
        self.assertIsNotNone(participant.user)
        activity_suggestion_configuration = ActivitySuggestionConfiguration.objects.get(user=participant.user)
        self.assertIsNotNone(activity_suggestion_configuration)

    def test_no_matching_enrollment_token(self):
        """
        If the enrollment token doesn't match an object in the database
        the response returns an error
        """
        response = self.client.post(reverse('participants-enroll'), {
            'enrollmentToken': 'doesnt-exist'
        })

        self.assertEqual(response.status_code, 401)

    def test_no_enrollment_token(self):
        response = self.client.post(reverse('participants-enroll'), {})

        self.assertEqual(response.status_code, 400)

    def test_matches_birth_year(self):
        Participant.objects.create(
            heartsteps_id = "test",
            enrollment_token = "token",
            birth_year = "1999"
        )

        response = self.client.post(reverse('participants-enroll'), {
            'enrollmentToken': 'token',
            'birthYear': '1999'
        })

        self.assertEqual(response.status_code, 200)

    def test_fail_enrollment_if_birth_year_but_not_tested(self):
        Participant.objects.create(
            heartsteps_id = "test",
            enrollment_token = "token",
            birth_year = "1999"
        )

        response = self.client.post(reverse('participants-enroll'), {
            'enrollmentToken': 'token'
        })

        self.assertEqual(response.status_code, 401)   
