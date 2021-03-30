import uuid
from django.db import models
from django.contrib.auth.models import User

class AuthenticationSession(models.Model):
    token = models.CharField(max_length=50, primary_key=True, unique=True, default=uuid.uuid4)    
    state = models.CharField(max_length=50, null=True, blank=True)
    redirect = models.CharField(max_length=255, null=True)
    
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
