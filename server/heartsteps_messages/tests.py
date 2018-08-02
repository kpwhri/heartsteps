from django.urls import reverse

from .models import Message
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

import uuid

class MessageRecievedTests(APITestCase):
    
    def test_marks_recieved(self):
        """
        Returns an authorization token and participant's heartsteps_id when a
        valid enrollment token is passed
        """
        user = User.objects.create(username="test")
        message = Message.objects.create(
            id = uuid.uuid4(),
            reciepent = user
        )

        self.client.force_authenticate(user=user)

        response = self.client.post(reverse('messages-recieved'), {
            'messageId': message.id
        })
        
        self.assertEqual(response.status_code, 201)
