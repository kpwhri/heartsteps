from django.db import models
from django.contrib.auth.models import User

class ServiceRequest(models.Model):
    user = models.ForeignKey(User)
    url = models.CharField(max_length=150)

    request_data = models.TextField()
    request_time = models.DateTimeField()

    response_code = models.IntegerField()
    response_data = models.TextField()
    response_time = models.DateTimeField()

    def __str__(self):
        return "%s (%d) %s" % (self.user, self.response_code, self.url)
