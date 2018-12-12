from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver

from locations.models import Location
from locations.services import LocationService

@receiver(post_save, sender=Location)
def post_save_suggested_time(sender, instance, *args, **kwargs):
    service = LocationService(instance.user)
    service.check_timezone_change()
