from django.db import models
from django.contrib.auth.models import User

class ContactInformation(models.Model):
    """
    Contact information for a user
    """
    user = models.OneToOneField(User)

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)