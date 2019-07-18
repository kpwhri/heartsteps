from django.test import TestCase

from contact.models import ContactInformation

from .models import User
from .models import Contact

class ContactTests(TestCase):

    def test_new_contact_information_creates_contact(self):
        user = User.objects.create(username='test')
        
        ContactInformation.objects.create(
            user = user,
            name = 'test',
            email = 'test@test.com',
            phone = '1234567890'
        )

        contact = Contact.objects.get()
        self.assertEqual(contact.number, '+11234567890')
        self.assertEqual(contact.user, user)
        self.assertTrue(contact.enabled)

    def test_contact_information_updates_contact(self):
        user = User.objects.create(username='test')
        contact_information = ContactInformation.objects.create(
            user = user,
            name = 'test',
            email = 'test@test.com',
            phone = '5555555555'
        )
        sms_contact = Contact.objects.get(user = user)
        sms_contact.enabled = False
        sms_contact.save()

        contact_information.phone = '1234567890'
        contact_information.save()

        sms_contact = Contact.objects.get(user = user)
        self.assertEqual(sms_contact.number, '+11234567890')
        self.assertFalse(sms_contact.enabled)
