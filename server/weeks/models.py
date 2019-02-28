import uuid
from datetime import timedelta, datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from locations.services import LocationService

User = get_user_model()

class Week(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(User)
    number = models.IntegerField(null=True)

    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['start_date']

    @property
    def id(self):
        return str(self.uuid)

    @property
    def start(self):
        return self.__localize_datetime(datetime(
            year = self.start_date.year,
            month = self.start_date.month,
            day = self.start_date.day,
            hour = 0,
            minute = 0
        ))

    @property
    def end(self):
        return self.__localize_datetime(datetime(
            year = self.end_date.year,
            month = self.end_date.month,
            day = self.end_date.day,
            hour = 23,
            minute = 59
        ))

    def __localize_datetime(self, time):
        service = LocationService(self.user)
        tz = service.get_current_timezone()
        return tz.localize(time)

    def __str__(self):
        return "%s to %s (%s)" % (self.start_date, self.end_date, self.user)

@receiver(pre_save, sender=Week)
def set_week_number(sender, instance, *args, **kwargs):
    if instance.number is None:
        number_of_weeks = Week.objects.filter(user=instance.user).count()
        instance.number = number_of_weeks + 1
