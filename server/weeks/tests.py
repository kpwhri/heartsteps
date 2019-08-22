from datetime import date, datetime
from unittest.mock import patch
import pytz
import json

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from rest_framework.test import APITestCase

from activity_summaries.models import Day
from locations.services import LocationService
from push_messages.services import PushMessageService
from weekly_reflection.signals import weekly_reflection

from .models import Week
from .models import WeekQuestion
from .models import WeeklyBarrier
from .models import WeeklyBarrierOption
from .models import User
from .services import WeekService
from .tasks import send_reflection

class WeeksModel(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

    def test_correctly_numbers_weeks(self):
        first_week = Week.objects.create(
            user = self.user,
            start_date = date(2018, 12, 1),
            end_date = date(2018, 12, 2)
        )
        second_week = Week.objects.create(
            user = self.user,
            start_date = date(2018, 12, 3),
            end_date = date(2018, 12, 4)
        )

        self.assertEqual(first_week.number, 1)
        self.assertEqual(second_week.number, 2)
    
    def test_sets_default_goal(self):
        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 3, 4),
            end_date = date(2019, 3, 10)
        )

        self.assertEqual(week.goal, 90)
    
    def test_activity_in_week_sets_goal(self):
        Day.objects.create(
            user = self.user,
            date = date(2019, 3, 2),
            total_minutes = 15
        )
        Day.objects.create(
            user = self.user,
            date = date(2019, 2, 27),
            total_minutes = 7
        )

        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 3, 4),
            end_date = date(2019, 3, 10)
        )

        self.assertEqual(week.goal, 40)

    def test_goal_not_over_150(self):
        Day.objects.create(
            user = self.user,
            date = date(2019, 3, 2),
            total_minutes = 150
        )
        Day.objects.create(
            user = self.user,
            date = date(2019, 2, 27),
            total_minutes = 70
        )

        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 3, 4),
            end_date = date(2019, 3, 10)
        )

        self.assertEqual(week.goal, 150)

class WeeksServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

        timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.current_timezone = timezone_patch.start()
        self.current_timezone.return_value = pytz.timezone('Etc/GMT-8')
        self.addCleanup(timezone_patch.stop)

    @patch.object(timezone, 'now')
    def test_initialize_weeks(self, now):
        now.return_value = pytz.UTC.localize(datetime(2019,2,28))
        self.user.date_joined = datetime(2019,2,1).astimezone(pytz.UTC)
        service = WeekService(user=self.user)

        service.update_weeks()
        
        week = service.get_current_week()
        self.assertEqual(week.number, 5)
        #assert first day of week is a monday
        self.assertEqual(week.start_date.weekday(), 0)
        #assert last day of week is a sunday
        self.assertEqual(week.end_date.weekday(), 6)

class WeekViewsTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            date_joined = datetime(2018, 12, 5).astimezone(pytz.UTC)
        )
        self.client.force_authenticate(user=self.user)

        timezone_patch = patch.object(timezone, 'now')
        self.now = timezone_patch.start()
        self.now.return_value = datetime(2019, 1, 6, 8).astimezone(pytz.UTC)
        self.addCleanup(timezone_patch.stop)

        location_service_patch = patch.object(LocationService, 'get_current_timezone')
        self.current_timezone = location_service_patch.start()
        self.current_timezone.return_value = pytz.UTC
        self.addCleanup(location_service_patch.stop)

        service = WeekService(self.user)
        service.update_weeks()

    def test_get_current_week(self):
        response = self.client.get(reverse('weeks-current'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 5)
        self.assertEqual(response.data['start'], '2018-12-31')
        self.assertEqual(response.data['end'], '2019-01-06')

    def test_get_week_2(self):
        response = self.client.get(reverse('weeks', kwargs={
            'week_number': 2
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 2)
        self.assertEqual(response.data['start'], '2018-12-10')
        self.assertEqual(response.data['end'], '2018-12-16')

    def test_get_next_week(self):
        response = self.client.get(reverse('weeks-next'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 6)
        self.assertEqual(response.data['start'], '2019-01-07')
        self.assertEqual(response.data['end'], '2019-01-13')


    def test_update_week_goal(self):
        response = self.client.post(reverse('weeks-current'), {
            'goal': 23,
            'confidence': 0.21
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 5)
        self.assertEqual(response.data['goal'], 23)
        self.assertEqual(response.data['confidence'], 0.21)

        service = WeekService(self.user)
        current_week = service.get_current_week()
        self.assertEqual(current_week.goal, 23)
        self.assertEqual(current_week.confidence, 0.21)

    def test_update_week_goal_no_confidence(self):
        response = self.client.post(reverse('weeks-current'), {
            'goal': 33
        })

        self.assertEqual(response.status_code, 200)
        service = WeekService(self.user)
        current_week = service.get_current_week()
        self.assertEqual(current_week.goal, 33)
        self.assertEqual(current_week.confidence, None)

    def test_update_next_week_goal(self):
        response = self.client.post(reverse('weeks-next'), {
            'goal': 500,
            'confidence': 0.001
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 6)
        self.assertEqual(response.data['goal'], 500)
        self.assertEqual(response.data['confidence'], 0.001)

    def test_update_week_error(self):
        response = self.client.post(reverse('weeks-current'), {})

        self.assertEqual(response.status_code, 400)

    @patch.object(WeekService, 'send_reflection')
    def test_sends_weekly_reflection(self, send_reflection):
        response = self.client.post(reverse('weeks-current-send'), {})

        self.assertEqual(response.status_code, 201)
        send_reflection.assert_called()

class WeekReflectionMessageSendTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

        Week.objects.create(
            user = self.user,
            start_date = date(2019, 3, 4),
            end_date = date(2019, 3, 10)
        )
        Week.objects.create(
            user = self.user,
            start_date = date(2019, 3, 11),
            end_date = date(2019, 3, 17)
        )

        timezone_patch = patch.object(timezone, 'now')
        self.now = timezone_patch.start()
        self.now.return_value = datetime(2019, 3, 9, 20).astimezone(pytz.UTC)
        self.addCleanup(timezone_patch.stop)

        send_notification_patch = patch.object(PushMessageService, 'send_notification')
        self.send_notification = send_notification_patch.start()
        self.addCleanup(send_notification_patch.stop)

        get_device_patch = patch.object(PushMessageService, 'get_device_for_user')
        get_device_patch.start()
        self.addCleanup(get_device_patch.stop)

        send_reflection_patch = patch.object(send_reflection, 'apply_async')
        self.send_reflection = send_reflection_patch.start()
        self.addCleanup(send_reflection_patch.stop)

    @patch.object(Week, 'get_default_goal', return_value=40)
    def test_sends_reflection(self, get_default_goal):
        weekly_reflection.send(User, username="test")

        self.send_notification.assert_called()
        data = self.send_notification.call_args[1]['data']
        self.assertEqual(data['type'], 'weekly-reflection')
        self.assertEqual(data['currentWeek']['id'], 1)
        self.assertEqual(data['nextWeek']['id'], 2)
        self.assertEqual(data['nextWeek']['goal'], 40)
        self.assertEqual(data['nextWeek']['start'], '2019-03-11')
        self.assertEqual(data['nextWeek']['end'], '2019-03-17')

        # Ensure next week's goal is set to default
        get_default_goal.assert_called()


class WeekSurveyTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

        WeekQuestion.objects.create(
            name = "sample question",
            label = "This is a sample question"
        )
        WeekQuestion.objects.create(
            name = "foobar",
            label = "Foo bar"
        )

    def test_every_week_gets_survey(self):
        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 4, 8),
            end_date = date(2019, 4, 14)
        )

        self.assertIsNotNone(week.survey)
        self.assertEqual(len(week.survey.questions), 2)

class WeeklyBarriersTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')

        WeeklyBarrierOption.objects.create(name = 'Poor weather')
        WeeklyBarrierOption.objects.create(name = 'Test')
        WeeklyBarrierOption.objects.create(name = 'Too busy')
        WeeklyBarrierOption.objects.create(name = 'Travel')

    def test_sets_week_barrier_options(self):
        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 8, 19),
            end_date = date(2019, 8, 25)
        )
        
        weekly_survey = week.survey
        self.assertEqual(week.barrier_options, ['Poor weather', 'Test', 'Too busy', 'Travel'])

    def test_sorts_by_barrier_use(self):
        previous_week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 8, 5),
            end_date = date(2019, 8, 11)
        )
        WeeklyBarrier.objects.create(
            week = previous_week,
            barrier = WeeklyBarrierOption.objects.get(name = 'Too busy')
        )

        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 8, 19),
            end_date = date(2019, 8, 25)
        )

        self.assertEqual(week.barrier_options, ['Too busy', 'Poor weather', 'Test', 'Travel'])

    def test_sorts_by_recent_barriers(self):
        previous_week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 8, 5),
            end_date = date(2019, 8, 11)
        )
        WeeklyBarrier.objects.create(
            week = previous_week,
            barrier = WeeklyBarrierOption.objects.get(name = 'Too busy')
        )
        last_week = Week.objects.create(
            user = self.user,
            start_date = date(2019,8,12),
            end_date = date(2019, 8, 18)
        )
        WeeklyBarrier.objects.create(
            week = last_week,
            barrier = WeeklyBarrierOption.objects.get(name = 'Travel')
        )

        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 8, 19),
            end_date = date(2019, 8, 25)
        )

        self.assertEqual(week.barrier_options, ['Travel', 'Too busy', 'Poor weather', 'Test'])

class WeekBarriersViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.client.force_authenticate(user=self.user)

        WeeklyBarrierOption.objects.create(name = 'Example barrier')
        WeeklyBarrierOption.objects.create(name = 'Travel')
        WeeklyBarrierOption.objects.create(name = 'Poor weather')

        self.last_week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 8, 12),
            end_date = date(2019, 8, 18)
        )
        self.current_week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 8, 19),
            end_date = date(2019, 8, 25)
        )

    def test_get_current_barriers(self):
        self.current_week.add_barrier('Example barrier')
        
        response = self.client.get(
            reverse('week-barriers', kwargs = {'week_number': self.current_week.number})
        )

        self.assertEqual(response.status_code,200)
        self.assertEqual(
            response.data,
            {
                'barriers': ['Example barrier'],
                'options': ['Example barrier', 'Poor weather', 'Travel'],
                'will_barriers_continue': None
            }
        )

    def test_set_current_barriers(self):
        self.current_week.add_barrier('Barrier to remove')

        response = self.client.post(
            reverse('week-barriers', kwargs = {'week_number': self.current_week.number}),
            {
                'barriers': ['Test barrier', 'Example barrier']
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['barriers'], ['Example barrier', 'Test barrier'])
        self.assertEqual(response.data['options'], ['Example barrier', 'Poor weather', 'Travel'])
        self.assertEqual(self.current_week.barriers, ['Example barrier', 'Test barrier'])
        test_barrier = WeeklyBarrierOption.objects.get(name='Test barrier')
        self.assertEqual(test_barrier.user, self.user)

    def test_update_will_barrier_continue(self):

        response = self.client.post(
            reverse('week-barriers', kwargs = {'week_number': self.current_week.number}),
            {
                'barriers': ['Test barrier', 'Example barrier'],
                'will_barriers_continue': 'unknown'
            }
        )

        self.assertEqual(response.status_code, 200)
        week = Week.objects.filter(user = self.user).last()
        self.assertEqual(week.will_barriers_continue, 'unknown')
