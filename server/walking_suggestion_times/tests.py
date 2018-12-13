from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from .models import SuggestionTime
from .signals import suggestion_times_updated

class SuggestionTimeReadView(APITestCase):

    def test_read_times(self):
        user = User.objects.create(username="test")
        SuggestionTime.objects.create(
            user = user,
            category = SuggestionTime.MORNING,
            hour = 14,
            minute = 30
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('walking-suggestion-times'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'morning': '14:30'
        })

class SuggestionTimeUpdateView(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

        self.patcher = patch.object(suggestion_times_updated, 'send')
        self.suggestions_times_updated_signal = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def get_times(self):
        return { 
            'morning': '7:45',
            'lunch': '12:15',
            'midafternoon': '15:30',
            'evening': '18:00',
            'postdinner': '21:00'
        }

    def test_create_times(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('walking-suggestion-times'),
            self.get_times(),
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        times = SuggestionTime.objects.filter(user=self.user).all()
        self.assertEqual(len(times), 5)

        afternoon_time = SuggestionTime.objects.get(user=self.user, category='midafternoon')
        self.assertEqual(afternoon_time.hour, 15)
        self.assertEqual(afternoon_time.minute, 30)

        self.suggestions_times_updated_signal.assert_called_with(SuggestionTime, username=self.user.username)

    def test_requires_all_activity_times(self):
        times = self.get_times()
        del times['midafternoon']

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('walking-suggestion-times'),
            times,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        times = SuggestionTime.objects.filter(user=self.user).all()
        self.assertEqual(len(times), 0)

        self.suggestions_times_updated_signal.assert_not_called()

    def test_updates_times(self):
        SuggestionTime.objects.create(
            user = self.user,
            category = 'midafternoon',
            hour = 15,
            minute = 22
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('walking-suggestion-times'),
            self.get_times(),
            format='json'
        )

        suggestion_times = SuggestionTime.objects.filter(user=self.user).all()
        self.assertEqual(len(suggestion_times), 5)
        midafternoon_suggestion_time = SuggestionTime.objects.get(user=self.user, category='midafternoon')
        self.assertEqual(midafternoon_suggestion_time.minute, 30)

        self.suggestions_times_updated_signal.assert_called_with(SuggestionTime, username=self.user.username)
