from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class PageView(models.Model):

    CLIENT = 'client'
    WEBSITE = 'website'
    PLATFORM_CHOICES = [
        (CLIENT, 'Client'),
        (WEBSITE, 'Website')
    ]

    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE
    )

    uri = models.CharField(max_length=250)
    time = models.DateTimeField()

    platform = models.CharField(max_length=20, null=True)
    version = models.CharField(max_length=15, null=True)
    build = models.CharField(max_length=15, null=True)

    created = models.DateTimeField(auto_now_add=True)
