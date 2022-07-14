from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save

class ActivityType(models.Model):
    name = models.CharField(max_length=500, unique=True)
    title = models.CharField(max_length=500)

    user = models.ForeignKey(User, null=True, on_delete = models.CASCADE, blank=True)

    def __str__(self):
        suffix = ''
        if self.user:
            suffix = '(%s)' % (self.user.username)
        if self.title:
            return '%s %s' % (self.title, suffix)
        else:
            return '%s %s' % (self.name, suffix)

@receiver(pre_save, sender=ActivityType)
def remove_spaces_from_name(sender, instance, *args, **kwargs):
    instance.name = instance.name.replace(' ', '_')
    return instance
