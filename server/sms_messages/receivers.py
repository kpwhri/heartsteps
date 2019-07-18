from django.dispatch import receiver
from django.db.models.signals import post_save

from contact.models import ContactInformation

from .models import Contact

@receiver(post_save, sender=ContactInformation)
def update_avaiable(sender, instance, *args, **kwargs):
    Contact.objects.update_or_create(
        user = instance.user,
        defaults = {
            'number': instance.phone_e164
        }
    )
