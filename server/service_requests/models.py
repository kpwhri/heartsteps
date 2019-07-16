from django.db import models
from django.contrib.auth.models import User

class ServiceRequest(models.Model):
    user = models.ForeignKey(User, null=True, editable=False)

    url = models.CharField(max_length=500, editable=False)
    name = models.CharField(max_length=150, editable=False)

    request_data = models.TextField(null=True, editable=False)
    request_time = models.DateTimeField(auto_now=True, editable=False)

    response_code = models.IntegerField(null=True, editable=False)
    response_data = models.TextField(null=True, editable=False)
    response_time = models.DateTimeField(null=True, editable=False)

    @property
    def sucessful(self):
        if self.response_code and self.response_code < 400:
            return True
        else:
            return False

    @property
    def duration(self):
        if self.response_time:
            if self.response_time > self.request_time:
                delta = self.response_time - self.request_time
            else:
                delta = self.request_time - self.response_time
            return delta.seconds
        else:
            return 0

    def __str__(self):
        if self.response_code:
            return "%s (%d) %s" % (self.user, self.response_code, self.url)
        else:
            return "%s %s" % (self.user, self.url)
