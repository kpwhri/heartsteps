import requests, json, pytz
from datetime import datetime, timedelta, date
from unittest.mock import patch, call

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth.models import User

from anti_sedentary.models import AntiSedentaryDecision
from behavioral_messages.models import MessageTemplate
from locations.models import Place
from service_requests.models import ServiceRequest
from push_messages.models import Message, MessageReceipt
from randomization.models import DecisionContext
from weather.models import WeatherForecast
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from fitbit_activities.models import FitbitDay, FitbitMinuteStepCount
from watch_app.models import StepCount as WatchStepCount

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
            service_initialized_date = date.today() - timedelta(days=1)
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
        assert 'totalStepsArray' in request_data
        assert 'preStepsMatrix' in request_data
        assert 'postStepsMatrix' in request_data

        expected_calls = [call(date - timedelta(days=offset)) for offset in range(3)]
        self.assertEqual(steps.call_args_list, expected_calls)
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
        decision.add_context(Place.HOME)
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
        self.assertEqual(request_data['location'], 2)

    def test_decision_throws_error_not_initialized(self):
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        decision.add_context(SuggestionTime.MORNING)
        self.configuration.service_initialized_date = None
        self.configuration.save()
        
        with self.assertRaises(WalkingSuggestionService.NotInitialized):
            self.service.decide(decision)

    @patch.object(WalkingSuggestionService, 'get_study_day', return_value=10)
    @patch.object(WalkingSuggestionService, 'get_clicks', return_value=20)
    @patch.object(WalkingSuggestionService, 'get_steps', return_value=500)
    @patch.object(WalkingSuggestionService, 'get_temperatures', return_value=[10, 10, 10, 10, 10])
    @patch.object(WalkingSuggestionService, 'get_pre_steps', return_value=[7, 7, 7, 7, 7])
    @patch.object(WalkingSuggestionService, 'get_post_steps', return_value=[700, 700, 700, 700, 700])
    @patch.object(WalkingSuggestionService, 'get_received_messages', return_value=[True, True, True, True, True])
    @patch.object(WalkingSuggestionService, 'get_availabilities', return_value=[False, False, False, False, False])
    @patch.object(WalkingSuggestionService, 'get_locations', return_value=[1, 1, 1, 1, 1])
    @patch.object(WalkingSuggestionService, 'get_previous_anti_sedentary_treatments', return_value=[False, False, False, False, False])
    def test_update(self, get_previous_anti_sedentary_treatments, get_locations, get_availabilities, get_received_messages, post_steps, pre_steps, temperatures, steps, clicks, study_day):
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
            'postStepsArray': [700, 700, 700, 700, 700],
            'availabilityArray': [False, False, False, False, False],
            'priorAntiArray': [False, False, False, False, False],
            'lastActivityArray': [True, True, True, True, True],
            'locationArray': [1, 1, 1, 1, 1]
        })

    def test_update_throws_error_not_initialized(self):
        self.configuration.service_initialized_date = None
        self.configuration.save()

        with self.assertRaises(WalkingSuggestionService.NotInitialized):
            self.service.update(timezone.now())

class StudyDayNumberTests(ServiceTestCase):

    def test_get_day_number_starts_at_one(self):
        today = date.today()
        day_number = self.service.get_study_day(today)

        self.assertEqual(day_number, 1)

    def test_get_day_number(self):
        later_date = timezone.now() + timedelta(days=5)
        day_number = self.service.get_study_day(later_date)

        self.assertEqual(day_number, 6)

    def test_works_with_date(self):
        later_date = date.today() + timedelta(days=10)
        day_number = self.service.get_study_day(later_date)

        self.assertEqual(day_number, 11)

class LocationContextTests(ServiceTestCase):
    
    def setUp(self):
        super().setUp()

    def testHomeLocation(self):
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        decision.add_context(Place.HOME)

        location_context = self.service.get_location_type(decision)

        self.assertEqual(location_context, 2)

    def testWorkLocation(self):
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        decision.add_context(Place.WORK)

        location_context = self.service.get_location_type(decision)

        self.assertEqual(location_context, 1)

    def testOtherLocation(self):
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )

        location_context = self.service.get_location_type(decision)

        self.assertEqual(location_context, 0)
        

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
            time = datetime(2018, 10, 10, 10, 10, tzinfo=pytz.utc)
        )
        decision.add_context('activity suggestion')
        decision.add_context(SuggestionTime.MORNING)

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

@override_settings(WALKING_SUGGESTION_DECISION_UNAVAILABLE_STEP_COUNT='100')
@override_settings(WALKING_SUGGESTION_DECISION_WINDOW_MINUTES=20)
class DecisionAvailabilityTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")  
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )      

    def create_step_count(self, steps, minutes_ago):
        WatchStepCount.objects.create(
            user = self.user,
            steps = steps,
            start = timezone.now() - timedelta(minutes=minutes_ago) - timedelta(minutes=5),
            end = timezone.now() - timedelta(minutes=minutes_ago)
        )

    def test_configuration_not_enabled(self):
        self.configuration.enabled = False
        self.configuration.save()
        decision = WalkingSuggestionDecision(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()

        self.assertFalse(available)
        decision = WalkingSuggestionDecision.objects.get()
        self.assertFalse(decision.available)
        self.assertEqual(decision.unavailable_reason, 'Walking suggestion configuration disabled')

    def test_no_step_counts(self):
        decision = WalkingSuggestionDecision(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()

        self.assertFalse(available)
        decision = WalkingSuggestionDecision.objects.get()
        self.assertFalse(decision.available)
        self.assertEqual(decision.unavailable_reason, 'No step counts recorded')

    def test_step_count_over_limit(self):
        self.create_step_count(10, 5)
        self.create_step_count(100, 10)
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()

        self.assertFalse(available)
        decision = WalkingSuggestionDecision.objects.get()
        self.assertFalse(decision.available)
        self.assertEqual(decision.unavailable_reason, 'Recent step count above 100')

    def test_step_count_was_over_limit(self):
        self.create_step_count(10, 5)
        self.create_step_count(100, 20)
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()

        self.assertTrue(available)
        decision = WalkingSuggestionDecision.objects.get()
        self.assertTrue(decision.available)

    def test_step_count(self):
        self.create_step_count(10, 5)
        self.create_step_count(10, 10)
        self.create_step_count(10, 15)
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()

        self.assertTrue(available)
        decision = WalkingSuggestionDecision.objects.get()
        self.assertTrue(decision.available)

    def test_not_available_when_recent_walking_suggestion_treated(self):
        recent_decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now() - timedelta(minutes=40),
            treated = True
        )
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()

        self.assertFalse(available)
        decision = WalkingSuggestionDecision.objects.get(id=decision.id)
        self.assertFalse(decision.available)
        self.assertEqual(decision.unavailable_reason, 'Recently treated walking suggestion decision')

    def test_not_available_when_recent_anti_sedentary_decision_treated(self):
        recent_decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = timezone.now() - timedelta(minutes=20),
            treated = True
        )
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()

        self.assertFalse(available)
        decision = WalkingSuggestionDecision.objects.get(id=decision.id)
        self.assertFalse(decision.available)
        self.assertEqual(decision.unavailable_reason, 'Recently treated anti sedentary decision')

    def test_available_after_push_message(self):
        self.create_step_count(10, 5)
        Message.objects.create(
            recipient = self.user,
            content = 'Foo'
        )
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()
        decision = WalkingSuggestionDecision.objects.get(id=decision.id)

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
