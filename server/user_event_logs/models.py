from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

User = get_user_model()

class EventLog(models.Model):

    SUCCESS = 'success'
    ERROR = 'error'
    INFO = 'info'
    DEBUG = 'debug'

    user = models.ForeignKey(
        User,
        null = True,
        related_name = '+',
        on_delete = models.CASCADE
    )
    status = models.CharField(max_length=25)

    message = models.CharField(max_length=250, null=True)
    data = models.JSONField(null=True)

class AuditEntry(models.Model):
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    username = models.CharField(max_length=256, null=True)

    def __unicode__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(action='user_logged_in', ip=ip, username=user.username)


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(action='user_logged_out', ip=ip, username=user.username)


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    AuditEntry.objects.create(action='user_login_failed', username=credentials.get('username', None))
