import requests, json, pytz
from datetime import datetime, timedelta
from unittest.mock import patch, call

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from randomization.models import Decision, DecisionContext
from weather.models import WeatherForecast
from fitbit_api.models import FitbitDay, FitbitAccount, FitbitMinuteStepCount

from activity_suggestions.services import ActivitySuggestionService
from activity_suggestions.models import ServiceRequest, Configuration, SuggestionTime

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
        self.requests_post.return_value = MockResponse(200, json.dumps({
            'success': 1 
        }))

    @override_settings(ACTIVITY_SUGGESTION_SERVICE_URL='http://example')
    def test_make_request(self):
        service = create_activity_suggestion_service()

        response = service.make_request('example',
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
        self.assertEqual(request_record.response_data, json.dumps({'success':1}))

    def test_returns_json(self):
        service = create_activity_suggestion_service()
        self.requests_post.return_value = MockResponse(200, json.dumps({
            'json':'parsed'
        }))

        response = service.make_request('example', data={'foo': 'bar'})

        self.assertEqual(response, {'json': 'parsed'})

class StudyDayNumberTests(TestCase):

    def test_get_day_number_starts_at_one(self):
        service = create_activity_suggestion_service()

        today = timezone.now()
        day_number = service.get_study_day(today)

        self.assertEqual(day_number, 1)

    def test_get_day_number(self):
        user = User.objects.create(username="test")
        user.date_joined = user.date_joined - timedelta(days=5)
        user.save()
        service = create_activity_suggestion_service()

        today = timezone.now()
        day_number = service.get_study_day(today)

        self.assertEqual(day_number, 6)

class ActivitySuggestionServiceTests(TestCase):

    def setUp(self):
        make_request_patch = patch.object(ActivitySuggestionService, 'make_request')
        self.addCleanup(make_request_patch.stop)
        self.make_request = make_request_patch.start()

    @override_settings(ACTIVITY_SUGGESTION_INITIALIZATION_DAYS=3)
    @patch.object(ActivitySuggestionService, 'get_clicks')
    @patch.object(ActivitySuggestionService, 'get_steps')
    @patch.object(ActivitySuggestionService, 'get_availabilities')
    @patch.object(ActivitySuggestionService, 'get_temperatures')
    @patch.object(ActivitySuggestionService, 'get_pre_steps')
    @patch.object(ActivitySuggestionService, 'get_post_steps')
    def test_initalization(self, post_steps, pre_steps, temperatures, availabilities, steps, clicks):
        service = create_activity_suggestion_service()

        date = datetime.today()
        service.initialize(date)

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        self.assertEqual(args[0], 'initialize')
        
        request_data = kwargs['data']
        assert 'appClicksArray' in request_data
        assert 'totalStepsArray' in request_data
        assert 'availMatrix' in request_data
        assert 'temperatureMatrix' in request_data
        assert 'preStepsMatrix' in request_data
        assert 'postStepsMatrix' in request_data

        expected_calls = [call(date - timedelta(days=offset)) for offset in range(3)]
        self.assertEqual(clicks.call_args_list, expected_calls)
        self.assertEqual(steps.call_args_list, expected_calls)
        self.assertEqual(availabilities.call_args_list, expected_calls)
        self.assertEqual(temperatures.call_args_list, expected_calls)
        self.assertEqual(pre_steps.call_args_list, expected_calls)
        self.assertEqual(post_steps.call_args_list, expected_calls)

        configuration = Configuration.objects.get(user__username='test')
        self.assertTrue(configuration.enabled)

    def test_decision(self):
        user = User.objects.create(username="test")
        configuration = Configuration.objects.create(
            user = user,
            enabled = True
        )
        decision = Decision.objects.create(
            user = user,
            time = timezone.now()
        )
        decision.add_context(SuggestionTime.MORNING)
        service = create_activity_suggestion_service()
        self.make_request.return_value = {
            'send': True,
            'probability': 1
        }

        service.decide(decision)

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        self.assertEqual(args[0], 'decision')
        request_data = kwargs['data']
        self.assertEqual(request_data['studyDay'], 1)
        assert 'location' in request_data

    def test_decision_throws_error_not_initialized(self):
        user = User.objects.create(username="test")
        decision = Decision.objects.create(
            user = user,
            time = timezone.now()
        )
        service = create_activity_suggestion_service()
        throws_error = False
        try:
            service.decide(decision)
        except ActivitySuggestionService.NotInitialized:
            throws_error = True
        self.assertTrue(throws_error)

    @patch.object(ActivitySuggestionService, 'get_study_day', return_value=10)
    @patch.object(ActivitySuggestionService, 'get_clicks', return_value=20)
    @patch.object(ActivitySuggestionService, 'get_steps', return_value=500)
    @patch.object(ActivitySuggestionService, 'get_temperatures', return_value=[10, 10, 10, 10, 10])
    @patch.object(ActivitySuggestionService, 'get_pre_steps', return_value=[7, 7, 7, 7, 7])
    @patch.object(ActivitySuggestionService, 'get_post_steps', return_value=[700, 700, 700, 700, 700])
    def test_update(self, post_steps, pre_steps, temperatures, steps, clicks, study_day):
        user = User.objects.create(username="test")
        configuration = Configuration.objects.create(
            user = user,
            enabled = True
        )
        service = create_activity_suggestion_service()

        date = datetime.today()
        service.update(date)

        self.make_request.assert_called()
        self.assertEqual(self.make_request.call_args[0][0], 'nightly')

        request_data = self.make_request.call_args[1]['data']
        self.assertEqual(request_data, {
            'studyDay': 10,
            'appClick': 20,
            'totalSteps': 500,
            'priorAnti': False,
            'lastActivity': False,
            'temperatureArray': [10, 10, 10, 10, 10],
            'preStepsArray': [7, 7, 7, 7, 7],
            'postStepsArray': [700, 700, 700, 700, 700]
        })

    def test_update_throws_error_not_initialized(self):
        service = create_activity_suggestion_service()
        throws_error = False
        try:
            service.update(timezone.now())
        except ActivitySuggestionService.NotInitialized:
            throws_error = True
        self.assertTrue(throws_error)

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

    def setUp(self):
        user = User.objects.create(username="test")
        account = FitbitAccount.objects.create(
            user = user,
            fitbit_user = "test"
        )
        decision = Decision.objects.create(
            user = user,
            time = datetime(2018, 10, 10, 10, 10, tzinfo=pytz.utc)
        )
        decision.add_context('activity suggestion')
        decision.add_context(SuggestionTime.MORNING)

        SuggestionTime.objects.create(
            user = user,
            category = SuggestionTime.LUNCH,
            hour = 12,
            minute = 30
        )
        SuggestionTime.objects.create(
            user = user,
            category = SuggestionTime.MIDAFTERNOON,
            hour = 15,
            minute = 00
        )
        SuggestionTime.objects.create(
            user = user,
            category = SuggestionTime.EVENING,
            hour = 17,
            minute = 30
        )

        decision = Decision.objects.create(
            user = user,
            time = datetime(2018, 10, 10, 22, 00, tzinfo=pytz.utc)
        )
        decision.add_context('activity suggestion')
        decision.add_context(SuggestionTime.POSTDINNER)
        day = FitbitDay.objects.create(
            account = account,
            date = datetime(2018,10,10)
        )
        FitbitMinuteStepCount.objects.create(
            day = day,
            account = account,
            time = datetime(2018, 10, 10, 10, 0, tzinfo=pytz.utc),
            steps = 50
        )
        FitbitMinuteStepCount.objects.create(
            day = day,
            account = account,
            time = datetime(2018, 10, 10, 9, 0, tzinfo=pytz.utc),
            steps = 10
        )
        FitbitMinuteStepCount.objects.create(
            day = day,
            account = account,
            time = datetime(2018, 10, 10, 10, 20, tzinfo=pytz.utc),
            steps = 120
        )
        FitbitMinuteStepCount.objects.create(
            day = day,
            account = account,
            time = datetime(2018, 10, 10, 21, 45, tzinfo=pytz.utc),
            steps = 10
        )
        FitbitMinuteStepCount.objects.create(
            day = day,
            account = account,
            time = datetime(2018, 10, 10, 22, 7, tzinfo=pytz.utc),
            steps = 10
        )
        # Following step counts shouldn't be considered
        FitbitMinuteStepCount.objects.create(
            day = day,
            account = account,
            time = datetime(2018, 10, 10, 9, 39, tzinfo=pytz.utc),
            steps = 50
        )
        FitbitMinuteStepCount.objects.create(
            day = day,
            account = account,
            time = datetime(2018, 10, 10, 22, 31, tzinfo=pytz.utc),
            steps = 50
        )

    def test_get_pre_steps(self):
        service = create_activity_suggestion_service()
        pre_steps = service.get_pre_steps(datetime(2018, 10, 10))
        
        self.assertEqual(pre_steps, [50, 0, 0, 0, 10])

    def test_get_post_steps(self):
        service = create_activity_suggestion_service()
        pre_steps = service.get_post_steps(datetime(2018, 10, 10))
        
        self.assertEqual(pre_steps, [120, 0, 0, 0, 10])

class TemperatureTests(TestCase):

    def setUp(self):
        user = User.objects.create(username="test")
        account = FitbitAccount.objects.create(
            user = user,
            fitbit_user = "test"
        )
        for time_category in SuggestionTime.TIMES:            
            decision = Decision.objects.create(
                user = user,
                time = datetime(2018, 10, 10, 10, 10, tzinfo=pytz.utc)
            )
            decision.add_context('activity suggestion')
            decision.add_context(time_category)
            forecast = WeatherForecast.objects.create(
                latitude = 1,
                longitude = 1,
                precip_probability = 0,
                precip_type = 'None',
                temperature = 50, # Only value that matters for test
                apparent_temperature = 100,
                time = timezone.now()
            )
            DecisionContext.objects.create(
                decision = decision,
                content_object = forecast
            )

    def test_temperature(self):
        service = create_activity_suggestion_service()

        temperatures = service.get_temperatures(datetime(2018, 10, 10))

        self.assertEqual(temperatures, [10, 10, 10, 10, 10])
