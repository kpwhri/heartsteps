from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from push_messages.models import Message, MessageReceipt

class MessageRecievedTests(APITestCase):
    
    def test_marks_received(self):
        """
        Will create message receipt for message
        """
        user = User.objects.create(username="test")
        message = Message.objects.create(
            recipient = user
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('messages-received'), [
            {
                'id': message.uuid,
                'received': '2007-07-12 04:07:02'
            }
        ], format='json')

        self.assertEqual(response.status_code, 200)
        receipt = MessageReceipt.objects.get()
        self.assertEqual(receipt.type, 'received')

    def test_if_unauthroized_cant_mark_received(self):
        """
        Will not allow a message receipt to be created if message belongs to other user
        """
        user = User.objects.create(username="test")
        message = Message.objects.create(
            recipient = User.objects.create(username="other-user")
        )
        
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('messages-received'), [
            {
                'id': message.uuid,
                'received': str(timezone.now())
            }
        ], format='json')

        self.assertEqual(response.status_code, 400)

    def test_receives_multiple_message_receipts(self):
        user = User.objects.create(username="test")
        message = Message.objects.create(
            recipient = user
        )
        other_message = Message.objects.create(
            recipient = user
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('messages-received'), [
            {
                'id': message.uuid,
                'received': '2007-07-07 07:07:07',
                'opened': '2007-07-07 07:07:08',
                'engaged': '2007-07-07 07:08:08'
            }, {
                'id': other_message.uuid,
                'received': '2010-10-10 10:10:10'
            }
        ], format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MessageReceipt.objects.count(), 4)