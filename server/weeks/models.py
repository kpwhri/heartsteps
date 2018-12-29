import uuid
from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

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

    def __str__(self):
        return "%s to %s (%s)" % (self.start_date, self.end_date, self.user)

@receiver(pre_save, sender=Week)
def set_week_number(sender, instance, *args, **kwargs):
    if instance.number is None:
        number_of_weeks = Week.objects.filter(user=instance.user).count()
        instance.number = number_of_weeks

@receiver(post_save, sender=Week)
def move_overlapping_weeks(sender, instance, *args, **kwargs):
    overlapping_weeks = Week.objects.exclude(
        uuid = instance.uuid
    ).filter(
        user = instance.user,
        start_date__lte = instance.end_date,
        start_date__gte = instance.start_date
    ).all()
    for week in overlapping_weeks:
        date_difference = week.end_date - week.start_date
        week.start_date = instance.end_date + timedelta(days=1)
        week.end_date = week.start_date + date_difference
        week.save()
