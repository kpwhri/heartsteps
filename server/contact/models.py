import phonenumbers

from django.db import models
from django.contrib.auth.models import User

class ContactInformation(models.Model):
    """
    Contact information for a user
    """
    user = models.OneToOneField(User)

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    @property
    def phone_e164(self):
        parsed_phone = phonenumbers.parse(self.phone, 'US')
        return phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)
