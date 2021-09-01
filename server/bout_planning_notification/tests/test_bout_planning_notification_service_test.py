from django.test import TestCase
from unittest.mock import patch

from bout_planning_notification.models import User
from bout_planning_notification.services import BoutPlanningNotificationService
from push_messages.models import Device, Message

class BoutPlanningNotificationServiceTest(TestCase):
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test")

    def tearDown(self):
        """Destroying testing user"""
        self.user.delete()

    def test_init_0(self):
        """Create testing service"""
        self.assertRaises(TypeError, BoutPlanningNotificationService)
        self.assertRaises(AssertionError, BoutPlanningNotificationService, None)
    
    def test_init_1(self):
        BoutPlanningNotificationService(self.user)
    
    def test_is_necessary_1(self):
        service = BoutPlanningNotificationService(self.user)
        self.assertTrue(service.is_necessary)

    @patch('push_messages.services.PushMessageService.send_notification')
    def test_send_notification_1(self, mock_send_notification):
        Device.objects.create(user=self.user, token="abc", type="onesignal", active=True)
        
        sample_body = 'Sample Bout Planning Body.'
        sample_title = 'Sample Bout Planning Title'
        sample_collapse_subject = 'bout_planninng'
        
        message1 = Message.objects.create(
            recipient=self.user,
            message_type=Message.NOTIFICATION,
            body=sample_body,
            title=sample_title,
            collapse_subject=sample_collapse_subject
        )
        
        mock_send_notification.return_value = message1
        service = BoutPlanningNotificationService(self.user)
        
        message2 = service.send_notification()
        
        self.assertEqual(message2.recipient, self.user)
        self.assertEqual(message2.message_type, Message.NOTIFICATION)
        self.assertEqual(message2.body, sample_body)
        self.assertEqual(message2.title, sample_title)
        self.assertEqual(message2.collapse_subject, sample_collapse_subject)

    @patch('push_messages.services.PushMessageService.send_notification')
    def test_send_notification_2(self, mock_send_notification):
        Device.objects.create(user=self.user, token="abc", type="onesignal", active=True)
        
        sample_body = 'test_body'
        sample_title = 'test_title'
        sample_collapse_subject = 'test_cs'
        
        message1 = Message.objects.create(
            recipient=self.user,
            message_type=Message.NOTIFICATION,
            body=sample_body,
            title=sample_title,
            collapse_subject=sample_collapse_subject
        )
        
        mock_send_notification.return_value = message1
        service = BoutPlanningNotificationService(self.user)
        
        message2 = service.send_notification(title=sample_title, body=sample_body, collapse_subject=sample_collapse_subject)
        
        self.assertEqual(message2.recipient, self.user)
        self.assertEqual(message2.message_type, Message.NOTIFICATION)
        self.assertEqual(message2.body, sample_body)
        self.assertEqual(message2.title, sample_title)
        self.assertEqual(message2.collapse_subject, sample_collapse_subject)
    
    @patch('push_messages.clients.OneSignalClient.send')
    def test_send_notification_3(self, mock_send):
        Device.objects.create(user=self.user, token="abc", type="onesignal", active=True)
        
        sample_body = 'test_body'
        sample_title = 'test_title'
        sample_collapse_subject = 'test_cs'
        sample_external_id = "abc123"
        
        mock_send.return_value = sample_external_id
        service = BoutPlanningNotificationService(self.user)
        
        message2 = service.send_notification(title=sample_title, body=sample_body, collapse_subject=sample_collapse_subject)
        
        self.assertEqual(message2.recipient, self.user)
        self.assertEqual(message2.message_type, Message.NOTIFICATION)
        self.assertEqual(message2.body, sample_body)
        self.assertEqual(message2.title, sample_title)
        self.assertEqual(message2.collapse_subject, sample_collapse_subject)
        self.assertEqual(message2.external_id, sample_external_id)
        