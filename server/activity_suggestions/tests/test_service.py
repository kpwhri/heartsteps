import requests
import json
from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from randomization.models import Decision
from fitbit_api.models import FitbitDay, FitbitAccount

from activity_suggestions.services import ActivitySuggestionService
from activity_suggestions.models import ServiceRequest, Configuration

def create_activity_suggestion_service():
    user, _ = User.objects.get_or_create(username="test")
    configuration, _ = Configuration.objects.get_or_create(
        user = user
    )
    return ActivitySuggestionService(configuration)

class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

class MakeRequestTests(TestCase):

    def setUp(self):
        requests_post_patch = patch.object(requests, 'post')
        self.addCleanup(requests_post_patch.stop)
        self.requests_post = requests_post_patch.start()
        self.requests_post.return_value = MockResponse(200, "success")

    @override_settings(ACTIVITY_SUGGESTION_SERVICE_URL='http://example')
    def test_make_request(self):
        service = create_activity_suggestion_service()

        service.make_request('example',
            data = {'foo': 'bar'}
        )

        self.requests_post.assert_called_with(
            'http://example/example',
            data = {
                'userId': 'test',
                'foo': 'bar'
            }
        )
        request_record = ServiceRequest.objects.get()
        self.assertEqual(request_record.request_data, json.dumps({
            'foo': 'bar',
            'userId': 'test'
        }))
        self.assertEqual(request_record.response_data, 'success')

class StudyDayNumberTests(TestCase):

    def test_get_day_number_starts_at_one(self):
        service = create_activity_suggestion_service()

        day_number = service.get_study_day_number()

        self.assertEqual(day_number, 1)

    def test_get_day_number(self):
        user = User.objects.create(username="test")
        user.date_joined = user.date_joined - timedelta(days=5)
        user.save()
        
        service = create_activity_suggestion_service()

        day_number = service.get_study_day_number()

        self.assertEqual(day_number, 6)

class ActivitySuggestionServiceTests(TestCase):

    def setUp(self):
        make_request_patch = patch.object(ActivitySuggestionService, 'make_request')
        self.addCleanup(make_request_patch.stop)
        self.make_request = make_request_patch.start()
        get_steps_patch = patch.object(ActivitySuggestionService, 'get_steps')
        self.addCleanup(get_steps_patch.stop)
        self.get_steps = get_steps_patch.start()
        self.get_steps.return_value = 30
        get_pre_steps_patch = patch.object(ActivitySuggestionService, 'get_pre_steps')
        self.addCleanup(get_pre_steps_patch.stop)
        self.get_pre_steps = get_pre_steps_patch.start()


    def test_initalization(self):
        service = create_activity_suggestion_service()

        service.initialize()

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        self.assertEqual(args[0], 'initialize')

        request_data = kwargs['data']
        self.assertEqual(len(request_data['appClicksArray']), 7)
        self.assertEqual(request_data['totalStepsArray'], [30 for i in range(7)])

    def test_decision(self):
        user = User.objects.create(username="test")
        decision = Decision.objects.create(
            user = user,
            time = timezone.now()
        )
        service = create_activity_suggestion_service()

        service.decide(decision)

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        self.assertEqual(args[0], 'decision')
        request_data = kwargs['data']
        self.assertEqual(request_data['studyDay'], 1)
        assert 'location' in request_data

    def test_update(self):
        service = create_activity_suggestion_service()

        service.update(datetime(2018, 11, 1))

        self.make_request.assert_called()
        self.assertEqual(self.make_request.call_args[0][0], 'nightly')

class GetStepsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        account = FitbitAccount.objects.create(
            user = self.user,
            fitbit_user = "test"
        )
        FitbitDay.objects.create(
            account = account,
            date = datetime(2018,10,10),
            total_steps = 400
        )

    def test_gets_steps(self):
        service = create_activity_suggestion_service()
        steps = service.get_steps(datetime(2018,10,10))
        assert steps == 400

    def test_gets_no_steps(self):
        service = create_activity_suggestion_service()
        steps = service.get_steps(datetime(2018,10,11))
        assert steps is None

class StepCountTests(TestCase):

    def test_get_pre_steps(self):
        service = create_activity_suggestion_service()

        pre_steps = service.get_pre_steps(datetime(2018, 10, 10))
        
