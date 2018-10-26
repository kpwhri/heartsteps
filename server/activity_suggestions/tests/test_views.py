from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from activity_suggestions.models import SuggestionTime

class SuggestionTimeUpdateView(APITestCase):

    def test_remove_existing_times_for_user(self):
        user = User.objects.create(username="test")
        SuggestionTime.objects.create(
            user = user,
            type = 'lunch',
            hour = 15,
            minute = 30
        )
        SuggestionTime.objects.create(
            user = user,
            type = 'evening',
            hour = 20,
            minute = 00
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse('activity_suggestions-times'),
            { 'times': [] },
            format='json'
        )

        times = SuggestionTime.objects.filter(user=user)
        
        self.assertEqual(len(times), 0)

    def test_create_times(self):
        user = User.objects.create(username="test")

        times = [
            { 'type': 'morning', 'hour': '7', 'minute': '0', 'timezone': 'US/Pacific' },
            { 'type': 'midafternoon', 'hour': '15', 'minute': '45', 'timezone': 'US/Pacific' }
        ]
        
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse('activity_suggestions-times'),
            { 'times': times },
            format='json'
        )
        

        times = SuggestionTime.objects.filter(user=user).all()
        self.assertEqual(len(times), 2)

        afternoon_time = SuggestionTime.objects.get(user=user, type='midafternoon')
        self.assertEqual(afternoon_time.hour, 15)
        self.assertEqual(afternoon_time.minute, 45)
