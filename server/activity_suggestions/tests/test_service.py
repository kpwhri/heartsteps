import requests
from datetime import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from randomization.models import Decision

from activity_suggestions.services import ActivitySuggestionService
from activity_suggestions.models import ActivityServiceRequest


class MockResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        return self.data

class MakeRequestTests(TestCase):

    def setUp(self):
        requests_post_patch = patch.object(requests, 'post')
        self.addCleanup(requests_post_patch.stop)
        self.requests_post = requests_post_patch.start()
        self.requests_post.return_value = MockResponse(200, {'foo':'bar'})

    @override_settings(ACTIVITY_SUGGESTION_SERVICE_URL='http://example')
    def test_make_request(self):
        user = User.objects.create(username="test")
        service = ActivitySuggestionService(user)
        example_payload = {'foo': 'bar'}

        service.make_request('example', example_payload)

        self.requests_post.assert_called_with(
            'http://example/example',
            data = example_payload
        )

    def test_saves_request_and_response(self):
        self.requests_post.return_value = MockResponse(200, {'example':'response'})
        user = User.objects.create(username="test")
        service = ActivitySuggestionService(user)

        service.make_request('example', {'foo': 'bar'})

        request_record = ActivityServiceRequest.objects.get(user=user)
        self.assertEqual(request_record.request_data['foo'], 'bar')
        self.assertEqual(request_record.response_data['example'], 'response')

class InitializeTests(TestCase):

    def setUp(self):
        make_request_patch = patch.object(ActivitySuggestionService, 'make_request')
        self.addCleanup(make_request_patch.stop)
        self.make_request = make_request_patch.start()

    def test_initalization(self):
        user = User.objects.create(username="test")
        service = ActivitySuggestionService(user)

        service.initialize(datetime(2018,11,1))

        self.make_request.assert_called()
        self.assertEqual(self.make_request.call_args[0][0], 'initialize')
        request_data = self.make_request.call_args[0][1]
        self.assertEqual(request_data['userId'], user.id)
        self.assertEqual(len(request_data['appClicksArray']), 7)
        self.assertEqual(len(request_data['totalStepsArray']), 7)

class ActivitySuggestionDecisionTests(TestCase):
    def setUp(self):
        make_request_patch = patch.object(ActivitySuggestionService, 'make_request')
        self.addCleanup(make_request_patch.stop)
        self.make_request = make_request_patch.start()

    def test_decision(self):
        user = User.objects.create(username="test")
        decision = Decision.objects.create(
            user = user,
            time = timezone.now()
        )
        service = ActivitySuggestionService(user)

        service.decide(decision)

        self.make_request.assert_called()
        self.assertEqual(self.make_request.call_args[0][0], 'decision')
        request_data = self.make_request.call_args[0][1]
        self.assertEqual(request_data['userId'], user.id)
        self.assertEqual(request_data['studyDay'], 2)
        assert 'location' in request_data

class NightlyUpdateTests(TestCase):
    def setUp(self):
        make_request_patch = patch.object(ActivitySuggestionService, 'make_request')
        self.addCleanup(make_request_patch.stop)
        self.make_request = make_request_patch.start()

    def test_update(self):
        user = User.objects.create(username="test")
        service = ActivitySuggestionService(user)

        service.update(datetime(2018, 11, 1))

        self.make_request.assert_called()
        self.assertEqual(self.make_request.call_args[0][0], 'nightly')
        request_data = self.make_request.call_args[0][1]
        self.assertEqual(request_data['userId'], [user.id])
