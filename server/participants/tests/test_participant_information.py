from unittest.mock import patch
import datetime
import pytz

from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

from days.models import Day

from participants.models import Participant
from participants.models import User
from participants.models import Study
from participants.models import Cohort

class ParticipantInformationTestCase(TestCase):

    def setUp(self):
        self.study = Study.objects.create(name='test')
        self.cohort = Cohort.objects.create(
            name = 'test',
            study = self.study
        )
        user = User.objects.create(username='test')
        user.date_joined = user.date_joined - datetime.timedelta(days=2)
        user.save()
        self.participant = Participant.objects.create(
            heartsteps_id = 'test',
            enrollment_token = 'test-test',
            user = user,
            cohort = self.cohort
        )
        Day.objects.create(
            user = user,
            date = datetime.date.today(),
            timezone = 'America/Los_Angeles'
        )

    def test_study_start_and_end_date_none_if_not_enrolled(self):
        participant = Participant.objects.create(heartsteps_id = 'example')
        
        self.assertEqual(participant.study_start, None)
        self.assertEqual(participant.study_end, None)

    def test_start_date_is_start_of_user_date_joined(self):
        two_days_ago = datetime.date.today() - datetime.timedelta(days=2)
        study_start_datetime = datetime.datetime(
            two_days_ago.year,
            two_days_ago.month,
            two_days_ago.day
        )
        tz = pytz.timezone('America/Los_Angeles')
        study_start_datetime = tz.localize(study_start_datetime)
        
        self.assertEqual(self.participant.study_start, study_start_datetime)

    def test_study_end_date_is_30_days_after_date_joined(self):
        end_datetime = self.participant.study_start + datetime.timedelta(days=31)

        self.assertEqual(self.participant.study_end, end_datetime)

    def test_study_end_date_calculated_from_cohort_date(self):
        self.cohort.study_length = 77
        self.cohort.save()
        end_datetime = self.participant.study_start + datetime.timedelta(days=78)

        self.assertEqual(self.participant.study_end, end_datetime)
        

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

    def test_returns_study_information(self):
        study = Study.objects.create(
            name = 'test',
            contact_name = 'test contact',
            contact_number = '(555) 555-5555',
            baseline_period = 10
        )
        cohort = Cohort.objects.create(
            name = 'test',
            study = study
        )
        user = User.objects.create(
            username='test',
            is_staff=True
        )
        Participant.objects.create(
            user = user,
            heartsteps_id = 'sample-id',
            enrollment_token = 'token',
            cohort = cohort
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('participants-information'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['studyContactName'], 'test contact')
        self.assertEqual(response.data['studyContactNumber'], '(555) 555-5555')
        self.assertEqual(response.data['baselinePeriod'], 10)

