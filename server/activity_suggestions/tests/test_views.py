from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from activity_suggestions.models import SuggestionTime, SuggestionTimeConfiguration

class SuggestionTimeUpdateView(APITestCase):

    def setUp(self):
        self.configuration = SuggestionTimeConfiguration.objects.create(
            user = User.objects.create(username="test")
        )

    def test_create_times(self):        
        self.client.force_authenticate(user=self.configuration.user)
        response = self.client.post(
            reverse('activity_suggestions-times'),
            { 
                'morning': '7:45',
                'lunch': '12:15',
                'midafternoon': '15:30',
                'evening': '18:00',
                'postdinner': '21:00'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        times = SuggestionTime.objects.filter(configuration=self.configuration).all()
        self.assertEqual(len(times), 5)

        afternoon_time = SuggestionTime.objects.get(configuration=self.configuration, type='midafternoon')
        self.assertEqual(afternoon_time.hour, 15)
        self.assertEqual(afternoon_time.minute, 30)

    def test_requires_all_activity_times(self):
        self.client.force_authenticate(user=self.configuration.user)
        response = self.client.post(
            reverse('activity_suggestions-times'),
            # missing midafternoon
            { 
                'morning': '7:45',
                'lunch': '12:15',
                'evening': '18:00',
                'postdinner': '21:00'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        times = SuggestionTime.objects.filter(configuration=self.configuration).all()
        self.assertEqual(len(times), 0)
