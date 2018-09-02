import json
from django.test import TestCase

from rest_framework.test import APITestCase
from django.urls import reverse

from django.contrib.auth.models import User
from .models import ReflectionTime

class ReflectionTimeView(APITestCase):

    def test_returns_reflection_time(self):
        user = User.objects.create(username="test")

        ReflectionTime.objects.create(
            user = user,
            day = 'sunday',
            time = '19:00'
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('weekly-reflection-time'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['day'], 'sunday')
        self.assertEqual(response.data['time'], '19:00')

    def test_returns_404_if_no_reflection_time(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('weekly-reflection-time'))

        self.assertEqual(response.status_code, 404)

    def test_create_reflection_time(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('weekly-reflection-time'), {
            'day': 'monday',
            'time': '8:30'
        })

        self.assertEqual(response.status_code, 200)

        reflection_time = ReflectionTime.objects.get(user=user, active=True)
        self.assertEqual(reflection_time.day, 'monday')
        self.assertEqual(reflection_time.time, '8:30')

    def test_updates_reflection_time(self):
        user = User.objects.create(username="test")
        ReflectionTime.objects.create(
            user = user,
            day = 'sunday',
            time = '19:00'
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('weekly-reflection-time'), {
            'day': 'monday',
            'time': '8:30'
        })

        self.assertEqual(response.status_code, 200)

        self.assertEqual(ReflectionTime.objects.filter(user=user).count(), 2)
        self.assertEqual(ReflectionTime.objects.filter(user=user, active=True).count(), 1)        