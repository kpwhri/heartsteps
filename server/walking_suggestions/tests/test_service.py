import requests
import json
import pytz
import time
from datetime import datetime, timedelta, date
import random
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
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
from page_views.models import PageView
from watch_app.models import StepCount as WatchStepCount

from walking_suggestions.services import WalkingSuggestionService, WalkingSuggestionDecisionService
from walking_suggestions.models import Configuration, WalkingSuggestionDecision, SuggestionTime
from walking_suggestions.models import PoolingServiceConfiguration

@override_settings(FITBIT_ACTIVITY_DAY_MINIMUM_WEAR_DURATION_MINUTES=20)
@override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example')
class ServiceTestCase(TestCase):

    def setUp(self):
        self.create_walking_suggestion_service()
        self.create_fitbit_account()

        time_patch = patch.object(time, 'sleep')
        time_patch.start()
        self.addCleanup(time_patch.stop)

    def create_walking_suggestion_service(self):
        self.user, _ = User.objects.get_or_create(username="test")
        self.configuration, _ = Configuration.objects.get_or_create(
            user = self.user,
            enabled = True,
            service_initialized_date = date.today() - timedelta(days=1)
        )
        self.service = WalkingSuggestionService(self.configuration)
        return self.service

    def create_fitbit_account(self):
        self.fitbit_account = FitbitAccount.objects.create(
            fitbit_user='test'
        )
        FitbitAccountUser.objects.create(
            account = self.fitbit_account,
            user = self.user
        )

    def create_page_views(self, day, amount):
        start = self.configuration.get_start_of_day(day)
        end = self.configuration.get_end_of_day(day)
        # Remove 100 so, we don't accidentally get to next day
        difference_seconds = (end - start).seconds - 100
        for x in range(amount):
            offset_seconds = random.randrange(difference_seconds)
            PageView.objects.create(
                user = self.user,
                time = start + timedelta(seconds=offset_seconds)
            )

    def create_heart_rate_range(self, start_datetime, minutes):
        for offset in range(minutes):
            FitbitMinuteHeartRate.objects.create(
                account = self.fitbit_account,
                time = (start_datetime + timedelta(minutes=offset)).astimezone(pytz.UTC),
                heart_rate = 70
            )

    def create_fitbit_day(self, day, step_count=500, wore_minutes=30):
        self.create_heart_rate_range(
            start_datetime = datetime(day.year, day.month, day.day, 11),
            minutes = wore_minutes
            )
        FitbitDay.objects.create(
            account = self.fitbit_account,
            date = day,
            step_count = step_count
        )

    def create_default_suggestion_times(self):
        SuggestionTime.objects.update_or_create(
            user = self.user,
            category = SuggestionTime.MORNING,
            defaults = {
                'hour': 8,
                'minute': 0
            }
        )
        SuggestionTime.objects.update_or_create(
            user = self.user,
            category = SuggestionTime.LUNCH,
            defaults = {
                'hour': 12,
                'minute': 0
            }
        )
        SuggestionTime.objects.update_or_create(
            user = self.user,
            category = SuggestionTime.MIDAFTERNOON,
            defaults = {
                'hour': 14,
                'minute': 0
            }
        )
        SuggestionTime.objects.update_or_create(
            user = self.user,
            category = SuggestionTime.EVENING,
            defaults = {
                'hour': 18,
                'minute': 0
            }
        )
        SuggestionTime.objects.update_or_create(
            user = self.user,
            category = SuggestionTime.POSTDINNER,
            defaults = {
                'hour': 20,
                'minute': 0
            }
        )
    
    def create_walking_suggestion_decision(self, category, available=True, treated=False, treatment_probability=0.2, location=None, temperature=None, pre_steps=100, post_steps=100):
        day = date.today()

        suggestion_time = SuggestionTime.objects.get(
            user = self.user,
            category = category
        )

        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            treated = treated,
            treatment_probability = treatment_probability,
            available = available,
            time = datetime(
                day.year,
                day.month,
                day.day,
                suggestion_time.hour,
                suggestion_time.minute
            ).astimezone(pytz.UTC)
        )
        decision.add_context(category)
        if location:
            decision.add_context(location)
        if not temperature:
            temperature = 65
        self.create_forecast(decision=decision, temperature=temperature)
        if treated:
            self.add_notification_to_decision(decision)
        FitbitMinuteStepCount.objects.create(
            account = self.fitbit_account,
            time = decision.time - timedelta(minutes=5),
            steps = pre_steps
        )
        FitbitMinuteStepCount.objects.create(
            account = self.fitbit_account,
            time = decision.time + timedelta(minutes=5),
            steps = post_steps
        )


    def create_forecast(self, decision, temperature):
        forecast = WeatherForecast.objects.create(
            latitude = 1,
            longitude = 1,
            precip_probability = 0,
            precip_type = 'None',
            temperature = temperature,
            apparent_temperature = 100,
            time = timezone.now()
        )
        DecisionContext.objects.create(
            decision = decision,
            content_object = forecast
        )

    def create_anti_sedentary_decision(self, time, treated=True):
        decision = AntiSedentaryDecision.objects.create(
            user = self.user,
            time = time,
            treated = True,
            treatment_probability = 0.25
        )
        if treated:
            self.add_notification_to_decision(decision)
    
    def add_notification_to_decision(self, decision, received=True):
        notification = Message.objects.create(
            recipient = self.user,
            message_type = Message.NOTIFICATION,
            content = 'foo'
        )
        if received:
            MessageReceipt.objects.create(
                message = notification,
                type = MessageReceipt.RECEIVED,
                time = decision.time + timedelta(minutes = 1)
            )
            decision.add_context_object(notification)


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
        super().setUp()
        self.create_default_suggestion_times()
        make_request_patch = patch.object(WalkingSuggestionService, 'make_request')
        self.addCleanup(make_request_patch.stop)
        self.make_request = make_request_patch.start()

    @override_settings(WALKING_SUGGESTION_INITIALIZATION_DAYS=3)
    def test_initialization(self):
        # Initializes a participant with 4 days of data. The second day the participant did not wear their fitbit.

        self.user.date_joined = timezone.now() - timedelta(days=7)
        self.user.save()
        self.configuration.pooling = True
        self.configuration.save()
        self.create_fitbit_day(date.today() - timedelta(days=3), step_count=500)
        self.create_fitbit_day(date.today() - timedelta(days=2), step_count=0, wore_minutes=0)
        self.create_fitbit_day(date.today() - timedelta(days=1), step_count=1000)
        self.create_fitbit_day(date.today(), step_count=1500)
        FitbitMinuteStepCount.objects.create(
            account = self.fitbit_account,
            time = datetime.now().replace(hour=20, minute=5).astimezone(pytz.UTC),
            steps = 50
        )
        self.assertEqual(WalkingSuggestionDecision.objects.count(), 0)
        
        today = date.today()
        self.service.initialize(today)

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        self.assertEqual(args[0], 'initialize')

        initialization_data = kwargs['data']
        self.assertEqual(initialization_data['date'], date.today().strftime('%Y-%m-%d'))
        self.assertTrue(initialization_data['pooling'])
        self.assertEqual(initialization_data['totalStepsArray'], [500, None, 1000, 1500])
        self.assertEqual(initialization_data['preStepsMatrix'], [
            {'steps':[None, None, None, None, None]},
            {'steps':[None, None, None, None, None]},
            {'steps':[None, None, None, None, None]},
            {'steps':[None, None, None, None, None]}
            ]
        )
        self.assertEqual(initialization_data['postStepsMatrix'], [
            {'steps':[None, None, None, None, None]},
            {'steps':[None, None, None, None, None]},
            {'steps':[None, None, None, None, None]},
            {'steps':[None,None,None,None,50]}
            ]
        )
        self.assertEqual(initialization_data['PriorAntiMatrix'], [
            {'priorAnti': [False, False, False, False, False, False]},
            {'priorAnti': [False, False, False, False, False, False]}
        ])
        self.assertEqual(initialization_data['DelieverMatrix'], [
            {'walking': [False, False, False, False, False]},
            {'walking': [False, False, False, False, False]}
        ])

        configuration = Configuration.objects.get(user__username='test')
        self.assertTrue(configuration.enabled)
        self.assertEqual(configuration.service_initialized_date, date.today())

        self.assertEqual(WalkingSuggestionDecision.objects.count(), 20)
        self.assertEqual(WalkingSuggestionDecision.objects.filter(imputed=True).count(), 20)

    def test_decision(self):
        PoolingServiceConfiguration.objects.create(
            user = self.user,
            use_pooling = True
        )
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        decision.add_context(SuggestionTime.MORNING)
        decision.add_context(Place.HOME)
        self.make_request.return_value = {
            'send': True,
            'probability': 0.123
        }

        self.service.decide(decision)

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        self.assertEqual(args[0], 'decision')
        request_data = kwargs['data']
        self.assertEqual(request_data['date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(request_data['studyDay'], 1)
        self.assertEqual(request_data['location'], 2)
        self.assertTrue(request_data['pooling'])
        decision = WalkingSuggestionDecision.objects.get()
        self.assertEqual(decision.treated, True)
        self.assertEqual(decision.treatment_probability, 0.123)

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

    def test_update(self):
        today = date.today()
        self.configuration.service_initialized_date = date.today() - timedelta(days=10)
        self.configuration.save()
        self.create_fitbit_day(date.today(), step_count=1500)
        # Create walking suggestion for all but morning suggestion time
        self.create_walking_suggestion_decision(
            category = SuggestionTime.LUNCH,
            location = Place.WORK
        )
        self.create_walking_suggestion_decision(
            category = SuggestionTime.MIDAFTERNOON,
            location = Place.WORK,
            treated = True
        )
        self.create_walking_suggestion_decision(
            category = SuggestionTime.EVENING,
            location = Place.OTHER,
            available = False,
            pre_steps = 1500,
            post_steps = 7
        )
        self.create_walking_suggestion_decision(
            category = SuggestionTime.POSTDINNER,
            treated = True,
            treatment_probability = 0.987,
            location = Place.HOME,
            temperature = 35,
            pre_steps = 20,
            post_steps = 120
        )
        dt = self.configuration.get_walking_suggestion_time(category = SuggestionTime.MORNING, day = today)
        dt = dt + timedelta(minutes = 10)
        self.create_anti_sedentary_decision(
            time = dt
        )
        dt = self.configuration.get_walking_suggestion_time(category = SuggestionTime.POSTDINNER, day = today)
        dt = dt + timedelta(minutes = 10)
        self.create_anti_sedentary_decision(
            time = dt
        )
        self.create_page_views(day = today, amount = 25)

        self.service.update(today)

        self.make_request.assert_called()
        self.assertEqual(self.make_request.call_args[0][0], 'nightly')
        request_data = self.make_request.call_args[1]['data']
        self.assertEqual(request_data['actionArray'], [False, False, True, False, True])
        self.assertEqual(request_data['availabilityArray'], [False, True, True, False, True])
        self.assertEqual(request_data['probArray'], [0, 0.2, 0.2, 0.2, 0.987])
        self.assertEqual(request_data['appClick'], 25)
        self.assertEqual(request_data['priorAntiArray'], [False, True, False, False, False, True])
        self.assertEqual(request_data['lastActivityArray'], [False, False, False, True, False])
        self.assertEqual(request_data['lastActivity'], True)
        self.assertEqual(request_data['totalSteps'], 1500)
        self.assertEqual(request_data['date'], today.strftime('%Y-%m-%d'))
        self.assertEqual(request_data['studyDay'], 10)
        self.assertEqual(request_data['locationArray'], [0, 1, 1, 0, 2])
        self.assertEqual(request_data['temperatureArray'], [None, 18.33, 18.33, 18.33, 1.67])
        self.assertEqual(request_data['preStepsArray'], [None, 100, 100, 1500, 20])
        self.assertEqual(request_data['postStepsArray'], [None, 100, 100, 7, 120])

    def test_update_throws_error_not_initialized(self):
        self.configuration.service_initialized_date = None
        self.configuration.save()

        with self.assertRaises(WalkingSuggestionService.NotInitialized):
            self.service.update(timezone.now())

@override_settings(WALKING_SUGGESTION_INITIALIZATION_DAYS=3)
class CanInitializeWalkingSuggestionService(ServiceTestCase):

    def setUp(self):
        super().setUp()
        self.create_default_suggestion_times()

        self.configuration.service_initialized_date = None
        self.configuration.save()

        self.user.date_joined = timezone.now() - timedelta(days=7)
        self.user.save()

        make_request_patch = patch.object(WalkingSuggestionService, 'make_request')
        self.make_request = make_request_patch.start()
        self.addCleanup(make_request_patch.stop)

    def test_enough_days(self):
        self.create_fitbit_day(date.today())
        self.create_fitbit_day(date.today() - timedelta(days=1))
        self.create_fitbit_day(date.today() - timedelta(days=2))

        self.service.initialize(date.today())
        
        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        data = kwargs['data']
        self.assertEqual(len(data['totalStepsArray']), 3)

    def test_allows_non_contiguous_days(self):
        self.create_fitbit_day(date.today())
        self.create_fitbit_day(date.today() - timedelta(days=1), 70, wore_minutes=10)
        self.create_fitbit_day(date.today() - timedelta(days=2), 20, wore_minutes=10)
        self.create_fitbit_day(date.today() - timedelta(days=3))
        self.create_fitbit_day(date.today() - timedelta(days=4))

        self.service.initialize(date.today())

        self.make_request.assert_called()
        args, kwargs = self.make_request.call_args
        data = kwargs['data']
        self.assertEqual(len(data['totalStepsArray']), 5)


    def test_not_enough_days(self):
        self.create_fitbit_day(date.today())
        self.create_fitbit_day(date.today() - timedelta(days=1), 90, wore_minutes=10)
        self.create_fitbit_day(date.today() - timedelta(days=2), 200, wore_minutes=10)

        try:
            self.service.initialize(date.today())
            self.fail('Initialization should have failed')
        except WalkingSuggestionService.UnableToInitialize:
            pass
        
        self.make_request.assert_not_called()

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
        self.fitbit_account = FitbitAccount.objects.create(
            fitbit_user = "test"
        )
        FitbitAccountUser.objects.create(
            account = self.fitbit_account,
            user = self.user
        )
        self.create_fitbit_day(
            day = date(2018,10,10),
            step_count = 400,
            wore_minutes = 30
        )

    def test_gets_steps(self):
        steps = self.service.get_steps(datetime(2018,10,10))
        self.assertEqual(steps, 400)

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

        SuggestionTime.objects.update_or_create(
            user = self.user,
            category = SuggestionTime.LUNCH,
            defaults = {
                'hour': 12,
                'minute': 30
            }
        )
        SuggestionTime.objects.update_or_create(
            user = self.user,
            category = SuggestionTime.MIDAFTERNOON,
            defaults = {
                'hour':15,
                'minute':00
            }
        )
        SuggestionTime.objects.update_or_create(
            user = self.user,
            category = SuggestionTime.EVENING,
            defaults = {
                'hour':17,
                'minute':30
            }
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

        FitbitMinuteHeartRate.objects.create(
            account = account,
            time = datetime(2018, 10, 10, 17, 20, tzinfo=pytz.utc),
            heart_rate = 20
        )
        FitbitMinuteHeartRate.objects.create(
            account = account,
            time = datetime(2018, 10, 10, 17, 40, tzinfo=pytz.utc),
            heart_rate = 20
        )

    def test_get_pre_steps(self):
        pre_steps = self.service.get_pre_steps(datetime(2018, 10, 10))
        
        self.assertEqual(pre_steps, [50, None, None, 0, 10])

    def test_get_post_steps(self):
        pre_steps = self.service.get_post_steps(datetime(2018, 10, 10))
        
        self.assertEqual(pre_steps, [120, None, None, 0, 10])

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
            self.create_forecast(
                decision = decision,
                temperature = 50
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

        ws_patch = patch.object(WalkingSuggestionDecisionService, 'send_message')
        ws_patch.start()
        self.addCleanup(ws_patch.stop)

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
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()

        self.assertFalse(available)
        decision = WalkingSuggestionDecision.objects.get()
        self.assertFalse(decision.available)
        self.assertTrue(decision.unavailable_disabled)

    def test_available_with_no_step_counts(self):
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        available = service.update_availability()

        self.assertFalse(available)
        decision = WalkingSuggestionDecision.objects.get()
        self.assertTrue(decision.available)
        self.assertFalse(decision.unavailable_no_step_count_data)

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
        self.assertTrue(decision.unavailable_not_sedentary)

    def test_step_count_was_over_limit(self):
        self.create_step_count(10, 5)
        self.create_step_count(100, 20)
        decision = WalkingSuggestionDecision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        service = WalkingSuggestionDecisionService(decision)

        service.update_availability()

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

        service.update_availability()

        decision = WalkingSuggestionDecision.objects.get()
        self.assertTrue(decision.available)

    def test_step_count_before_walking_suggestion_time(self):
        now = timezone.now()
        suggestion_time = now + timedelta(minutes=10)
        # Destroy default suggestion times, so test logic will work
        SuggestionTime.objects.all().delete()
        SuggestionTime.objects.create(
            user = self.user,
            category = SuggestionTime.MIDAFTERNOON,
            hour = suggestion_time.hour,
            minute = suggestion_time.minute
        )

        WalkingSuggestionDecisionService.make_decision(
            datetime = now,
            user=self.user
        )

        decision = WalkingSuggestionDecision.objects.get()
        self.assertEqual(decision.category, SuggestionTime.MIDAFTERNOON)

    def test_single_walking_suggestion_per_period(self):
        now = timezone.now()
        suggestion_time = now + timedelta(minutes=10)
        SuggestionTime.objects.create(
            user = self.user,
            category = SuggestionTime.MIDAFTERNOON,
            hour = suggestion_time.hour,
            minute = suggestion_time.minute
        )
        WalkingSuggestionDecisionService.make_decision(
            datetime = now - timedelta(minutes=5),
            user=self.user
        )

        try:
            WalkingSuggestionDecisionService.make_decision_now(
                user = self.user
            )
            self.fail('Should not have made second walking suggestion decision')
        except WalkingSuggestionDecisionService.RandomizationUnavailable:
            pass
        self.assertEqual(WalkingSuggestionDecision.objects.count(), 1)

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
