from unittest.mock import patch
from django.test import TestCase

from django.contrib.auth.models import User

from push_messages.models import Message, Device
from push_messages.functions import send_notification, send_data

class MessageSendTest(TestCase):

    def make_user(self):
        user = User.objects.create(username="test")
        Device.objects.create(
            user = user,
            token = 'example-token',
            type = 'web',
            active = True
        )
        return user

    # @patch('requests.post')
    # def test_send_notification(self, request_post):
    #     user = self.make_user()
    #     # send_notification(user, "Example Title", "Example Body")

    #     # request_post.assert_called()

    # @patch('requests.post')
    # def test_send_data(self, request_post):
    #     user = self.make_user()
    #     # send_data(user, {'some': 'data'})

    #     # request_post.assert_called()