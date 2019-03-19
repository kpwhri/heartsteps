from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class PageView(models.Model):

    user = models.ForeignKey(User)

    uri = models.CharField(max_length=250)
    time = models.DateTimeField()

    created = models.DateTimeField(auto_now_add=True)
