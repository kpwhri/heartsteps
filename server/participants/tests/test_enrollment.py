from unittest.mock import patch
from datetime import date

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

from participants.models import Participant
from participants.models import User
from participants.services import ParticipantService

class LogoutViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username = 'test'
        )
        self.participant = Participant.objects.create(
            heartsteps_id = 'test',
            enrollment_token = 'test-test',
            user = self.user
        )
        self.participant_service = ParticipantService(participant = self.participant)

    def test_logout(self):
        self.participant_service.get_authorization_token()
        self.client.force_authenticate(self.user)

        response = self.client.post(reverse('participants-logout'), {})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.participant_service.has_authorization_token())


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

    def test_add_dash_to_enrollment_token(self):
        Participant.objects.create(
            heartsteps_id = "test",
            enrollment_token = "abcd-efgh",
            birth_year = "1980"
        )

        response = self.client.post(reverse('participants-enroll'), {
            'enrollmentToken': 'abcdefgh',
            'birthYear': 1980
        })

        self.assertEqual(response.status_code, 200)

    def test_study_start_date_is_set_when_enrolled(self):
        Participant.objects.create(
            heartsteps_id = 'test',
            enrollment_token = 'token',
            birth_year = '1999'
        )

        response = self.client.post(reverse('participants-login'), {
            'enrollmentToken': 'token',
            'birthYear': 1999
        })

        participant = Participant.objects.get(heartsteps_id='test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(participant.study_start_date, date.today())

    def test_study_start_date_is_not_updated_if_already_set(self):
        Participant.objects.create(
            heartsteps_id = 'test',
            enrollment_token = 'token',
            birth_year = '1999',
            study_start_date = date(2021,5,10)
        )

        response = self.client.post(reverse('participants-login'), {
            'enrollmentToken': 'token',
            'birthYear': 1999
        })

        participant = Participant.objects.get(heartsteps_id='test')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(participant.study_start_date, date.today())
