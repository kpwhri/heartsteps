from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

User = get_user_model()

class EventLog(models.Model):
    SUCCESS = 'SCS'
    ERROR = 'ERR'
    INFO = 'INF'
    DEBUG = 'DBG'
    STATES = [
        (SUCCESS, SUCCESS),
        (ERROR, ERROR),
        (INFO, INFO),
        (DEBUG, DEBUG),
    ]

    user = models.ForeignKey(
        User,
        null = True,
        related_name = '+',
        on_delete = models.CASCADE
    )
    status = models.CharField(max_length=3, choices=STATES)
    action = models.TextField(null=True, blank=True)
    # data = models.JSONField(null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    # Creates a user log. Status can be any of the four STATES listed above, with a max length of 3 characters.
    def log(user, action, status):
        if user is None:
            user, _ = User.objects.get_or_create(username="__system_log")
        else:
            if isinstance(user, str):
                user_q = User.objects.filter(username=user)
                if user_q.exists():
                    user = user_q.get()
                else:
                    raise User.DoesNotExist()
            elif isinstance(user, User):
                pass
            else:
                assert isinstance(user, User), "user argument must be None or an instance of User"
        if not isinstance(action, str):
            action = str(action)
        
        if not (status, status) in EventLog.STATES:
            raise ValueError("status should be called via EventLog.XXXX")
        
        return EventLog.objects.create(user=user, status=status, action=action)

    def debug(user, action):
        EventLog.log(user, action, EventLog.DEBUG)
    
    def info(user, action):
        EventLog.log(user, action, EventLog.INFO)
    
    def error(user, action):
        EventLog.log(user, action, EventLog.ERROR)
    
    def success(user, action):
        EventLog.log(user, action, EventLog.SUCCESS)
        

    def get_logs(user, status=None):
        base_query = EventLog.objects.filter(user=user).order_by('-timestamp')

        if not status is None:
            base_query = base_query.filter(status=status)

        return list(base_query.all())
    
    def __str__(self):
        return "{} {} {} {}".format(str(self.user), self.timestamp, self.status, self.action)


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
