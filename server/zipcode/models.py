from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ZipCodeRequestHistory(models.Model):
    zipcode = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response_code = models.CharField(max_length=3, null=True)
    response_message = models.TextField(null=True)

    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    state = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=50, null=True)
    when_requested = models.DateTimeField(auto_now_add=True)
    
