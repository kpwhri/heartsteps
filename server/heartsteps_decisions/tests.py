from django.urls import reverse

from .models import Decision
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

class DecisionView(APITestCase):
    
    def test_creates_decision(self):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('heartsteps-decisions'))
        
        self.assertEqual(response.status_code, 201)

        decision = Decision.objects.get(user=user, a_it=None)
        self.assertIsNotNone(decision)
