from django.dispatch import receiver
from django.db.models.signals import post_save

from sms_messages.models import Contact as SMSContact

from .models import User
from .signals import initialize_participant

@receiver(initialize_participant, sender=User)
def update_avaiable(sender, user, *args, **kwargs):
    try:
        sms_contact = SMSContact.objects.get(user = user)
        sms_contact.enabled = True
        sms_contact.save()
    except SMSContact.DoesNotExist:
        pass
