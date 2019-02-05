import requests, json, pytz
from datetime import datetime, timedelta
from unittest.mock import patch, call

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from behavioral_messages.models import MessageTemplate
from service_requests.models import ServiceRequest
from push_messages.models import Message, MessageReceipt
from randomization.models import DecisionContext
from weather.models import WeatherForecast
from fitbit_api.models import FitbitDay, FitbitAccount, FitbitAccountUser, FitbitMinuteStepCount

from walking_suggestions.services import WalkingSuggestionService, WalkingSuggestionDecisionService
from walking_suggestions.models import Configuration, WalkingSuggestionDecision, SuggestionTime

@override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example')
class ServiceTestCase(TestCase):

    def setUp(self):
        self.create_walking_suggestion_service()

    def create_walking_suggestion_service(self):
        self.user, _ = User.objects.get_or_create(username="test")
        self.configuration, _ = Configuration.objects.get_or_create(
            user = self.user,
            enabled = True,
            service_initialized = True
        )
        self.service = WalkingSuggestionService(self.configuration)
        return self.service

class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

class MakeRequestTests(ServiceTestCase):

    def setUp(self):
        self.create_walking_suggestion_service()

        requests_post_patch = patch.object(requests, 'post')
        self.addCleanup(requests_post_patch.stop)
        self.requests_post = requests_post_patch.start()
        self.requests_post.return_value = MockResponse(200, json.dumps({
            'success': 1 
        }))

    def test_make_request(self):
        example_request = {
            'foo': 'bar',
            'userID': 'test'
        }

        response = self.service.make_request('example',
            data = {'foo': 'bar'}
        )

        self.requests_post.assert_called_with(
            'http://example/example',
            json = example_request
        )
        request_record = ServiceRequest.objects.get()
        self.assertEqual(request_record.request_data, json.dumps(example_request))
        self.assertEqual(request_record.response_data, json.dumps({'success':1}))

    def test_returns_json(self):
        self.requests_post.return_value = MockResponse(200, json.dumps({
            'json':'parsed'
        }))

        response = self.service.make_request('example', data={'foo': 'bar'})

        self.assertEqual(response, {'json': 'parsed'})

class WalkingSuggestionServiceTests(ServiceTestCase):

    def setUp(self):
        self.create_walking_suggestion_service()
        make_request_patch = patch.object(WalkingSuggestionService, 'make_request')
        self.addCleanup(make_request_patch.stop)
        self.make_request = make_request_patch.start()

    @override_settings(WALKING_SUGGESTION_INITIALIZATION_DAYS=3)
    @patch.object(WalkingSuggestionService, 'get_clicks')
    @patch.object(WalkingSuggestionService, 'get_steps')
    @patch.object(WalkingSuggestionService, 'get_availabilities')
    @patch.object(WalkingSuggestionService, 'get_temperatures')
    @patch.object(WalkingSuggestionService, 'get_pre_steps')
    @patch.object(WalkingSuggestionService, 'get_post_steps')
    def test_initalization(self, post_steps, pre_steps, temperatures, availabilities, steps, clicks):
        date = datetime.today()
        self.service.initialize(date)

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
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        decision.add_context(SuggestionTime.MORNING)
        self.make_request.return_value = {
            'send': True,
            'probability': 1
        }

        self.service.decide(decision)

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        self.assertEqual(args[0], 'decision')
        request_data = kwargs['data']
        self.assertEqual(request_data['studyDay'], 1)
        assert 'location' in request_data

    def test_decision_throws_error_not_initialized(self):
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        decision.add_context(SuggestionTime.MORNING)
        self.configuration.service_initialized = False
        self.configuration.save()
        
        with self.assertRaises(WalkingSuggestionService.NotInitialized):
            self.service.decide(decision)

    @patch.object(WalkingSuggestionService, 'get_study_day', return_value=10)
    @patch.object(WalkingSuggestionService, 'get_clicks', return_value=20)
    @patch.object(WalkingSuggestionService, 'get_steps', return_value=500)
    @patch.object(WalkingSuggestionService, 'get_temperatures', return_value=[10, 10, 10, 10, 10])
    @patch.object(WalkingSuggestionService, 'get_pre_steps', return_value=[7, 7, 7, 7, 7])
    @patch.object(WalkingSuggestionService, 'get_post_steps', return_value=[700, 700, 700, 700, 700])
    def test_update(self, post_steps, pre_steps, temperatures, steps, clicks, study_day):
        date = datetime.today()
        self.service.update(date)

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
        self.configuration.service_initialized = False
        self.configuration.save()

        with self.assertRaises(WalkingSuggestionService.NotInitialized):
            self.service.update(timezone.now())

class StudyDayNumberTests(ServiceTestCase):

    def test_get_day_number_starts_at_one(self):
        today = timezone.now()
        day_number = self.service.get_study_day(today)

        self.assertEqual(day_number, 1)

    def test_get_day_number(self):
        self.user.date_joined = self.user.date_joined - timedelta(days=5)
        self.user.save()

        today = timezone.now()
        day_number = self.service.get_study_day(today)

        self.assertEqual(day_number, 6)

class GetStepsTests(ServiceTestCase):

    def setUp(self):
        self.create_walking_suggestion_service()
        account = FitbitAccount.objects.create(
            fitbit_user = "test"
        )
        FitbitAccountUser.objects.create(
            account = account,
            user = self.user
        )
        day = FitbitDay.objects.create(
            account = account,
            date = datetime(2018,10,10),
            step_count = 400
        )

    def test_gets_steps(self):
        steps = self.service.get_steps(datetime(2018,10,10))
        assert steps == 400

    def test_gets_no_steps(self):
        steps = self.service.get_steps(datetime(2018,10,11))
        assert steps is None

class StepCountTests(ServiceTestCase):

    def setUp(self):
        self.create_walking_suggestion_service()
        account = FitbitAccount.objects.create(
            fitbit_user = "test"
        )
        FitbitAccountUser.objects.create(
            user = self.user,
            account = account
        )
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = datetime(2018, 10, 10, 10, 10, tzinfo=pytz.utc)
        )
        decision.add_context('activity suggestion')
        decision.add_context(SuggestionTime.MORNING)

        SuggestionTime.objects.create(
            user = self.user,
            category = SuggestionTime.LUNCH,
            hour = 12,
            minute = 30
        )
        SuggestionTime.objects.create(
            user = self.user,
            category = SuggestionTime.MIDAFTERNOON,
            hour = 15,
            minute = 00
        )
        SuggestionTime.objects.create(
            user = self.user,
            category = SuggestionTime.EVENING,
            hour = 17,
            minute = 30
        )

        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = datetime(2018, 10, 10, 22, 00, tzinfo=pytz.utc)
        )
        decision.add_context('activity suggestion')
        decision.add_context(SuggestionTime.POSTDINNER)
        FitbitMinuteStepCount.objects.create(
            account = account,
            time = datetime(2018, 10, 10, 10, 0, tzinfo=pytz.utc),
            steps = 50
        )
        FitbitMinuteStepCount.objects.create(
            account = account,
            time = datetime(2018, 10, 10, 9, 0, tzinfo=pytz.utc),
            steps = 10
        )
        FitbitMinuteStepCount.objects.create(
            account = account,
            time = datetime(2018, 10, 10, 10, 20, tzinfo=pytz.utc),
            steps = 120
        )
        FitbitMinuteStepCount.objects.create(
            account = account,
            time = datetime(2018, 10, 10, 21, 45, tzinfo=pytz.utc),
            steps = 10
        )
        FitbitMinuteStepCount.objects.create(
            account = account,
            time = datetime(2018, 10, 10, 22, 7, tzinfo=pytz.utc),
            steps = 10
        )
        # Following step counts shouldn't be considered
        FitbitMinuteStepCount.objects.create(
            account = account,
            time = datetime(2018, 10, 10, 9, 39, tzinfo=pytz.utc),
            steps = 50
        )
        FitbitMinuteStepCount.objects.create(
            account = account,
            time = datetime(2018, 10, 10, 22, 31, tzinfo=pytz.utc),
            steps = 50
        )

    def test_get_pre_steps(self):
        pre_steps = self.service.get_pre_steps(datetime(2018, 10, 10))
        
        self.assertEqual(pre_steps, [50, 0, 0, 0, 10])

    def test_get_post_steps(self):
        pre_steps = self.service.get_post_steps(datetime(2018, 10, 10))
        
        self.assertEqual(pre_steps, [120, 0, 0, 0, 10])

class TemperatureTests(ServiceTestCase):

    def setUp(self):
        self.create_walking_suggestion_service()
        account = FitbitAccount.objects.create(
            fitbit_user = "test"
        )
        FitbitAccountUser.objects.create(
            account = account,
            user = self.user
        )

        for time_category in SuggestionTime.TIMES:            
            decision = WalkingSuggestionDecision.objects.create(
                user = self.user,
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
        temperatures = self.service.get_temperatures(datetime(2018, 10, 10))

        self.assertEqual(temperatures, [10, 10, 10, 10, 10])

class DecisionAvailabilityTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.account = FitbitAccount.objects.create(
            fitbit_user = "test"
        )
        FitbitAccountUser.objects.create(
            account = self.account,
            user = self.user 
        )
        FitbitMinuteStepCount.objects.create(
            account = self.account,
            time = timezone.now() - timedelta(minutes=15),
            steps = 10
        )
        FitbitMinuteStepCount.objects.create(
            account = self.account,
            time = timezone.now() - timedelta(minutes=30),
            steps = 120
        )

        self.decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        self.decision.add_context("activity suggestion")
        self.decision.add_context(SuggestionTime.MORNING)

    def test_fitbit_steps(self):
        service = WalkingSuggestionDecisionService(self.decision)

        available = service.determine_availability()

        self.assertTrue(available)

    def test_fitbit_steps_unavailable(self):
        FitbitMinuteStepCount.objects.create(
            account = self.account,
            time = timezone.now() - timedelta(minutes=5),
            steps = 300
        )
        service = WalkingSuggestionDecisionService(self.decision)

        available = service.determine_availability()

        self.assertFalse(available)

    def test_no_fitbit_step_counts(self):
        FitbitMinuteStepCount.objects.all().delete()
        service = WalkingSuggestionDecisionService(self.decision)

        available = service.determine_availability()

        self.assertTrue(available)

class TestLastWalkingSuggestion(ServiceTestCase):

    def setUp(self):
        self.create_walking_suggestion_service()
        times = [8, 12, 15, 17, 19]
        now = timezone.now()
        for time_category in SuggestionTime.TIMES:
            decision = WalkingSuggestionDecision.objects.create(
                user = self.user,
                time = datetime(
                    year = now.year,
                    month = now.month,
                    day = now.day,
                    hour = times[SuggestionTime.TIMES.index(time_category)],
                    minute = 0,
                    tzinfo = pytz.utc
                )
            )
            decision.add_context("activity suggestion")
            decision.add_context(time_category)

    def test_gets_previous_suggestion_received(self):
        decision = WalkingSuggestionDecision.objects.get(tags__tag=SuggestionTime.MIDAFTERNOON)
        previous_decision = self.service.get_previous_decision(decision)

        self.assertEqual(previous_decision.time.hour, 12)

    def test_returns_none_for_first_suggestion_time(self):
        decision = WalkingSuggestionDecision.objects.get(tags__tag=SuggestionTime.MORNING)
        previous_decision = self.service.get_previous_decision(decision)

        self.assertEqual(previous_decision, None)

    def test_previous_message_was_received(self):
        previous_decision = WalkingSuggestionDecision.objects.get(tags__tag=SuggestionTime.MORNING)
        message = Message.objects.create(
            recipient = previous_decision.user,
            content = "Hey",
            message_type = Message.NOTIFICATION
        )
        DecisionContext.objects.create(
            decision = previous_decision,
            content_object = message
        )
        MessageReceipt.objects.create(
            message = message,
            time = timezone.now(),
            type = MessageReceipt.RECEIVED
        )

        decision = WalkingSuggestionDecision.objects.get(tags__tag=SuggestionTime.LUNCH)
        was_received = self.service.previous_decision_was_received(decision)

        self.assertTrue(was_received)

    def test_previous_message_was_not_received(self):
        decision = WalkingSuggestionDecision.objects.get(tags__tag=SuggestionTime.LUNCH)

        was_received = self.service.previous_decision_was_received(decision)

        self.assertFalse(was_received)
