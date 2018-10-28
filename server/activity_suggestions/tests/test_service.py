import requests
import json
from datetime import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from randomization.models import Decision

from activity_suggestions.services import ActivitySuggestionService
from activity_suggestions.models import ServiceRequest


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
        user = User.objects.create(username="test")
        service = ActivitySuggestionService()

        service.make_request('example',
            user = user,
            data = {'foo': 'bar'}
        )

        self.requests_post.assert_called_with(
            'http://example/example',
            data = {
                'userId': 'test',
                'foo': 'bar'
            }
        )
        request_record = ServiceRequest.objects.get(user=user)
        self.assertEqual(request_record.request_data, json.dumps({
            'foo': 'bar',
            'userId': 'test'
        }))
        self.assertEqual(request_record.response_data, 'success')

class InitializeTests(TestCase):

    def setUp(self):
        make_request_patch = patch.object(ActivitySuggestionService, 'make_request')
        self.addCleanup(make_request_patch.stop)
        self.make_request = make_request_patch.start()

    def test_initalization(self):
        user = User.objects.create(username="test")
        service = ActivitySuggestionService()

        service.initialize(user, datetime.now())

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        self.assertEqual(args[0], 'initialize')
        self.assertEqual(kwargs['user'], user)
        request_data = kwargs['data']
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
        service = ActivitySuggestionService()

        service.decide(decision)

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        self.assertEqual(args[0], 'decision')
        request_data = kwargs['data']
        self.assertEqual(request_data['studyDay'], 2)
        assert 'location' in request_data

class NightlyUpdateTests(TestCase):
    def setUp(self):
        make_request_patch = patch.object(ActivitySuggestionService, 'make_request')
        self.addCleanup(make_request_patch.stop)
        self.make_request = make_request_patch.start()

    def test_update(self):
        user = User.objects.create(username="test")
        service = ActivitySuggestionService()

        service.update(user, datetime(2018, 11, 1))

        self.make_request.assert_called()
        self.assertEqual(self.make_request.call_args[0][0], 'nightly')
