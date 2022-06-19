from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
import inspect, os

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

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp'])
        ]

    def whoami():
        stack = inspect.stack()
    
        parent_stack = stack[1][0]
        func_name = parent_stack.f_code.co_name
        line_no = parent_stack.f_lineno
        file_name =  parent_stack.f_code.co_filename
        file_pos = "{}:{}".format(file_name, line_no)
        
        if 'self' in parent_stack.f_locals:
            class_name = parent_stack.f_locals['self'].__class__.__name__
            
            return "{}({}.{}())".format(file_pos, class_name, func_name)
        else:
            return "{}(static {}())".format(file_pos, func_name)

    def __ancestor(max_depth=7):
        stack = inspect.stack()
        
        stack.pop(0) # __ancestor()
        stack.pop(0) # debug()
        
        stack_str_arr = []
        
        for a_stack in stack:
            a_stack = a_stack[0]
            func_name = a_stack.f_code.co_name
            line_no = a_stack.f_lineno
            full_file_name = a_stack.f_code.co_filename
            file_path, file_name = os.path.split(full_file_name)
            if 'self' in a_stack.f_locals:
                class_name = a_stack.f_locals['self'].__class__.__name__
                stack_str = "{}.{}({}:{})".format(class_name, func_name, file_name, line_no)
            else:
                stack_str = "{}({}:{})".format(func_name, file_name, line_no)
            stack_str_arr.append(stack_str)
            
            if len(stack_str_arr) > max_depth:
                break
    
        return " <- ".join(stack_str_arr)
    
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
                    action = "[{}] {}".format(user, action)
                    user = None
            elif isinstance(user, User):
                pass
            else:
                action = "[{}] {}".format(user, action)
                user = None
        if not isinstance(action, str):
            action = str(action)
        
        if not (status, status) in EventLog.STATES:
            raise ValueError("status should be called via EventLog.XXXX")
        
        return EventLog.objects.create(user=user, status=status, action=action)

    def debug(user, action=""):
        msg = "{} ({})".format(action, EventLog.__ancestor())
            
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
