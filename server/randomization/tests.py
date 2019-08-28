from datetime import datetime
from datetime import timedelta
from unittest.mock import patch
import json

import pytz
from timezonefinder import TimezoneFinder

from django.test import override_settings
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase

from behavioral_messages.models import ContextTag as MessageTag
from behavioral_messages.models import MessageTemplate
from locations.models import Location, Place
from locations.services import LocationService
from push_messages.models import Message as PushMessage, Device
from push_messages.services import PushMessageService
from watch_app.services import StepCountService as WatchAppStepCountService
from weather.models import WeatherForecast
from weather.services import WeatherService

from .models import User
from .models import Decision
from .models import DecisionContext
from .models import DecisionRating
from .services import DecisionContextService
from .services import DecisionMessageService

class DecisionMessageTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

        is_sedentary_patch = patch.object(Decision, '_is_sedentary')
        self.is_sedentary_patch = is_sedentary_patch.start()
        self.is_sedentary_patch.return_value = True
        self.addCleanup(is_sedentary_patch.stop)

    def make_decision_service(self):
        decision = Decision.objects.create(
            user = self.user,
            time = timezone.now()
        )
        return DecisionMessageService(decision)

    def test_decision_picks_message_template(self):
        decision_service = self.make_decision_service()
        message_template = MessageTemplate.objects.create(body="Test message")

        message = decision_service.create_message_template()

        self.assertEqual(message.body, message_template.body)

    def test_decision_picks_message_template_with_matching_tags(self):
        tag = MessageTag.objects.create(tag="tag")

        message_template = MessageTemplate.objects.create(body="Test message")
        message_template.context_tags.add(tag)

        MessageTemplate.objects.create(body="Not this message")

        decision_service = self.make_decision_service()
        decision_service.add_context("tag")
        
        message = decision_service.create_message_template()

        self.assertNotEqual(message.body, "Not this message")

    def test_decision_picks_most_specific_matching_template(self):
        tag = MessageTag.objects.create(tag="tag")
        specific_tag = MessageTag.objects.create(tag="specific tag")

        template = MessageTemplate.objects.create(body="Test message")
        template.context_tags.add(tag)

        specific_template = MessageTemplate.objects.create(body="Specific test message")
        specific_template.context_tags.add(tag, specific_tag)

        MessageTemplate.objects.create(body="Generic message")
        MessageTemplate.objects.create(body="Generic message 2")

        decision_service = self.make_decision_service()
        decision_service.add_context("tag")
        decision_service.add_context("specific tag")
        
        message = decision_service.create_message_template()

        self.assertEqual(message.body, specific_template.body)

    def test_decision_ignores_context_that_is_not_message_tag(self):
        tag = MessageTag.objects.create(tag="tag")
        template = MessageTemplate.objects.create(body="Test message")
        template.context_tags.add(tag)

        decision_service = self.make_decision_service()
        decision_service.add_context("tag")
        decision_service.add_context("not a message tag")
        
        message = decision_service.create_message_template()

        self.assertEqual(message.body, "Test message")

    @patch.object(PushMessageService, 'send_notification')
    def test_sends_message(self, send_notification):
        decision_service = self.make_decision_service()
        Device.objects.create(
            user = self.user,
            active = True,
            token ="123"
        )
        message_template = MessageTemplate.objects.create(body="Test message")
        push_message = PushMessage.objects.create(
            recipient = self.user,
            content = "foo",
            message_type = PushMessage.NOTIFICATION
        )
        send_notification.return_value = push_message

        decision_service.send_message()

        send_notification.assert_called_with(
            message_template.body,
            title=message_template.title,
            data={
                'randomizationId': str(decision_service.decision.id)
            } 
        )

        context_objects = [obj.content_object for obj in DecisionContext.objects.all()]
        self.assertIn(message_template, context_objects)
        self.assertIn(push_message, context_objects)

    def test_is_unavailabe_if_notification_sent_in_last_hour(self):
        decision_service = self.make_decision_service()
        message = PushMessage.objects.create(
            recipient = decision_service.decision.user,
            message_type = PushMessage.NOTIFICATION
        )
        message.created = decision_service.decision.time - timedelta(minutes=30)
        message.save()

        decision_service.update_availability()

        self.assertFalse(decision_service.decision.available)

    def test_is_availabe_if_no_notification_last_hour(self):
        decision_service = self.make_decision_service()
        message = PushMessage.objects.create(
            recipient = decision_service.decision.user,
            message_type = PushMessage.NOTIFICATION
        )
        message.created = decision_service.decision.time - timedelta(minutes=90)
        message.save()
        message = PushMessage.objects.create(
            recipient = decision_service.decision.user,
            message_type = PushMessage.DATA
        )
        message.created = decision_service.decision.time - timedelta(minutes=30)
        message.save()

        decision_service.update_availability()

        self.assertTrue(decision_service.decision.available)

class DecisionContextTest(TestCase):
    """
    Ensure decisions are created and gather context from associated services.
    """

    def setUp(self):
        self.user = User.objects.create(username="test")

        get_last_location_patch = patch.object(LocationService, 'get_last_location')
        self.addCleanup(get_last_location_patch.stop)
        self.get_last_location = get_last_location_patch.start()
        self.get_last_location.return_value = Location.objects.create(
            longitude = 123.123,
            latitude = 42.42,
            user = self.user,
            time = timezone.now()
        )

    def make_decision_service(self, time=None):
        if not time:
            time = timezone.now()
        decision = Decision.objects.create(
            user = self.user,
            time = time
        )
        return DecisionContextService(decision)

    @patch.object(DecisionContextService, 'get_location_context', return_value="home")
    @patch.object(DecisionContextService, 'get_weather_context', return_value="outdoor")
    def test_decision_adds_context(self, get_weather_context, get_location_context):
        """
        Decision service adds correct tags to decision and saves related objects
        """
        decision_service = self.make_decision_service()
        
        decision_service.update_context()

        get_weather_context.assert_called()
        get_location_context.assert_called()
        context_tags_text = [tag.tag for tag in decision_service.decision.tags.all()]
        self.assertIn('home', context_tags_text)
        self.assertIn('outdoor', context_tags_text)

    @patch.object(LocationService, 'categorize_location', return_value="home")
    def test_get_location_context(self, categorize_location):
        decision_service = self.make_decision_service()
        
        location_type = decision_service.get_location_context()

        categorize_location.assert_called()
        self.assertEqual(location_type, "home")
        self.get_last_location.assert_called()
        self.assertEqual(DecisionContext.objects.filter(decision=decision_service.decision).count(), 1)

    def test_get_location_fails(self):
        decision_service = self.make_decision_service()

        location_type = decision_service.get_location_context()

        self.assertEqual(location_type, "other")

    @patch.object(LocationService, 'get_last_location')
    def test_get_location_returns_location_in_decision_context(self, get_last_location):
        get_last_location.return_value = None
        decision_service = self.make_decision_service()
        location = Location.objects.create(
            latitude = 22.22,
            longitude = 42.42,
            user = decision_service.user,
            time = timezone.now()
        )
        DecisionContext.objects.create(
            decision = decision_service.decision,
            content_object = location
        )
        
        returned_location = decision_service.get_location()

        get_last_location.assert_not_called()
        self.assertEqual(returned_location.id, location.id)

    @patch.object(WeatherService,'get_forecast_context')
    @patch.object(WeatherService, 'make_forecast')
    def test_get_weather_context(self, make_forecast, get_forecast_context):
        fake_weather_object = User.objects.create(username="totally_fake")
        make_forecast.return_value = fake_weather_object
        get_forecast_context.return_value = 'outdoors'
        decision_service = self.make_decision_service()
        decision_service.location = Location.objects.create(
            latitude = 22.22,
            longitude = 42.42,
            user = decision_service.user,
            time = timezone.now()
        )

        weather_context = decision_service.get_weather_context()

        self.assertEqual(weather_context, "outdoors")
        get_forecast_context.assert_called_with(fake_weather_object)
        make_forecast.assert_called_with(
            latitude = 22.22,
            longitude = 42.42,
            time = decision_service.decision.time
        )
        # there should only be one saved object
        saved_decision_forecast = DecisionContext.objects.get(decision=decision_service.decision).content_object
        self.assertEqual(saved_decision_forecast, fake_weather_object)

    @patch.object(WeatherService, 'get_average_forecast_context')
    @patch.object(WeatherService, 'make_forecast')
    def test_get_weather_context_no_location(self, make_forecast, get_average_forecast_context):
        """
        Decision service imputes weather when no location is found
        """
        def unknown_location():
            raise LocationService.UnknownLocation()
        self.get_last_location.side_effect = unknown_location
        fake_weather_object = User.objects.create(username="totally_fake")
        make_forecast.return_value = fake_weather_object
        get_average_forecast_context.return_value = 'outdoors'
        decision_service = self.make_decision_service()
        Place.objects.create(
            user = decision_service.user,
            type = 'home',
            latitude = 123.456,
            longitude = 42.42
        )
        Place.objects.create(
            user = decision_service.user,
            type = 'work',
            latitude = 123.123,
            longitude = 42.05
        )

        weather_context = decision_service.get_weather_context()

        self.assertEqual(weather_context, "outdoors")
        get_average_forecast_context.assert_called()
        self.assertIn(fake_weather_object, get_average_forecast_context.call_args[0][0])

    def test_add_weekday_context(self):
        #day is a Wednesday
        decision_time = datetime(2018, 10, 10, 10, 10).astimezone(pytz.utc)
        decision_service = self.make_decision_service(decision_time)

        context = decision_service.get_week_context()
        
        self.assertEqual(context, "weekday")

    def test_add_weekend_context(self):
        # Day is Saturady
        decision_time = datetime(2018, 10, 13, 13, 13).astimezone(pytz.utc)
        decision_service = self.make_decision_service(decision_time)

        context = decision_service.get_week_context()
        
        self.assertEqual(context, "weekend")

    @patch.object(TimezoneFinder, 'timezone_at', return_value="US/Pacific")
    def test_corrects_weekend_for_timezone(self, timezone_at):
        # Day is early monday morning UTC - late sunday evening PST
        decision_time = datetime(2018, 10, 15, 2).astimezone(pytz.utc)
        decision_service = self.make_decision_service(decision_time)
        location = Location.objects.create(
            latitude = 123.123,
            longitude = 42.42,
            user = decision_service.user,
            time = timezone.now()
        )
        DecisionContext.objects.create(
            decision = decision_service.decision,
            content_object = location
        )

        context = decision_service.get_week_context()
        
        self.assertEqual(context, "weekend")
        timezone_at.assert_called_with(lat=123.123, lng=42.42)

class DecisionActivityTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')

        is_sedentary_patch = patch.object(Decision, '_is_sedentary')
        self.is_sedentary = is_sedentary_patch.start()
        self.is_sedentary.return_value = True
        self.addCleanup(is_sedentary_patch.stop)

        notification_recently_sent_patch = patch.object(Decision, 'is_notification_recently_sent')
        self.notification_recently_sent = notification_recently_sent_patch.start()
        self.notification_recently_sent.return_value = False
        self.addCleanup(notification_recently_sent_patch.stop)

    def format_time_range(self, start, end):
        return start.strftime('%Y-%m-%d@%H:%M') + end.strftime('%Y-%m-%d@%H:%M')

    @override_settings(RANDOMIZATION_RECENTLY_ACTIVE_DURATION_MINUTES=35)
    @override_settings(RANDOMIZATION_RECENTLY_ACTIVE_STEP_COUNT_THRESHOLD=500)
    @patch.object(WatchAppStepCountService, 'get_step_count_between', return_value=600)
    def test_unavailable_if_recently_active(self, get_step_count_between):
        decision = Decision.objects.create(
            user = self.user,
            time = timezone.now()
        )

        decision.update()

        self.assertFalse(decision.available)
        self.assertTrue(decision.unavailable_recently_active)
        
        formatted_step_count_calls = []
        for call in get_step_count_between.call_args_list:
            formatted_step_count_calls.append(
                self.format_time_range(
                    start = call[1]['start'],
                    end = call[1]['end']
                )
            )
        expected_call = self.format_time_range(
            start = decision.time - timedelta(minutes=35),
            end = decision.time
        )
        self.assertIn(expected_call, formatted_step_count_calls)

    @override_settings(RANDOMIZATION_RECENTLY_ACTIVE_DURATION_MINUTES=35)
    @override_settings(RANDOMIZATION_RECENTLY_ACTIVE_STEP_COUNT_THRESHOLD=500)
    @patch.object(WatchAppStepCountService, 'get_step_count_between', return_value=400)
    def test_available_if_not_recently_active(self, get_step_count_between):
        decision = Decision.objects.create(
            user = self.user,
            time = timezone.now()
        )

        decision.update()

        self.assertTrue(decision.available)
        self.assertFalse(decision.unavailable_recently_active)

class DecisionRatingTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.client.force_authenticate(user=self.user)

        self.decision = Decision.objects.create(
            user = self.user,
            time = timezone.now()
        )

    def get_decision_rating_url(self):
        return reverse(
            'randomization-rating',
            kwargs = {
                'decision_id': str(self.decision.id)
            }
        )

    def test_get_decision_rating(self):
        DecisionRating.objects.create(
            decision = self.decision,
            liked = True,
            comments = 'This is a test'
        )

        response = self.client.get(
            self.get_decision_rating_url()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['liked'], True)
        self.assertEqual(response.data['comments'], 'This is a test')

    def test_create_decision_rating(self):

        response = self.client.post(
            self.get_decision_rating_url(),
            {
                'liked': False,
                'comments': 'Test comments'
            },
            format = 'json'
        )

        self.assertEqual(response.status_code, 201)
        decision_rating = DecisionRating.objects.get()
        self.assertEqual(decision_rating.decision.id, self.decision.id)
        self.assertFalse(decision_rating.liked)
        self.assertEqual(decision_rating.comments, 'Test comments')

    def test_updates_decision_rating(self):
        DecisionRating.objects.create(
            decision = self.decision,
            liked = False,
            comments = 'Test'
        )

        response = self.client.post(
            self.get_decision_rating_url(),
            {
                'liked': None,
                'comments': None
            },
            format = 'json'
        )

        self.assertEqual(response.status_code, 201)
        decision_rating = DecisionRating.objects.get()
        self.assertEqual(decision_rating.liked, None)
        self.assertEqual(decision_rating.comments, None)

    def test_comments_are_optional(self):
        response = self.client.post(
            self.get_decision_rating_url(),
            {
                'liked': None
            },
            format = 'json'
        )

        self.assertEqual(response.status_code, 201)
        