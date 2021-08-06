from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class FeatureFlags(models.Model):
    class FeatureFlagExistsException(Exception):
        pass
    
    class FeatureFlagsDoNotExistException(Exception):
        pass
    
    class Meta:
        verbose_name = 'Feature Flags'
        verbose_name_plural = 'Feature Flags'

    uuid = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    flags = models.TextField(default="")

    def __str__(self):
        return self.user.username

    def create(user, flags=""):
        assert isinstance(user, User), "user argument should be an instance of User class: {}".format(type(user))
        assert isinstance(flags, str), "flags argument should be a string: {}".format(type(flags))
        
        if FeatureFlags.exists(user):
            raise FeatureFlags.FeatureFlagExistsException
        
        return FeatureFlags.objects.create(user=user, flags=flags)
    
    def exists(user):
        assert isinstance(user, User), "user argument should be an instance of User class: {}".format(type(user))
        
        return FeatureFlags.objects.filter(user=user).exists()
    
    def update(user, flags):
        assert isinstance(user, User), "user argument should be an instance of User class: {}".format(type(user))
        assert isinstance(flags, str), "flags argument should be a string: {}".format(type(flags))
        
        if not FeatureFlags.exists(user):
            raise FeatureFlags.FeatureFlagsDoNotExistException
        
        FeatureFlags.objects.filter(user=user).update(flags=flags)
        
        return FeatureFlags.objects.filter(user=user).first()