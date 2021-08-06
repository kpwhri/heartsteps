from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class FeatureFlags(models.Model):
    class FeatureFlagsExistException(Exception):
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

    def create(user:User, flags:str=""):
        """Create a new feature flag.
        
        Arguments: 
            user(User)
            flags(str) optional
        
        Raises:
            FeatureFlags.FeatureFlagsExistException : if the flag exists
        """
        assert isinstance(user, User), "user argument should be an instance of User class: {}".format(type(user))
        assert isinstance(flags, str), "flags argument should be a string: {}".format(type(flags))
        
        if FeatureFlags.exists(user):
            raise FeatureFlags.FeatureFlagsExistException
        
        return FeatureFlags.objects.create(user=user, flags=flags)
    
    def exists(user:User):
        """check if the feature flags exist

        Args:
            user (User)

        Returns:
            boolean: if the feature flags exist
        """
        assert isinstance(user, User), "user argument should be an instance of User class: {}".format(type(user))
        
        return FeatureFlags.objects.filter(user=user).exists()
    
    def update(user:User, flags:str):
        """updates if the feature flags exist

        Args:
            user (User)
            flags (str): new feature flags

        Raises:
            FeatureFlags.FeatureFlagsDoNotExistException: if the featureFlags do not exist

        Returns:
            FeatureFlags object: updated feature flags
        """
        assert isinstance(user, User), "user argument should be an instance of User class: {}".format(type(user))
        assert isinstance(flags, str), "flags argument should be a string: {}".format(type(flags))
        
        if not FeatureFlags.exists(user):
            raise FeatureFlags.FeatureFlagsDoNotExistException
        
        FeatureFlags.objects.filter(user=user).update(flags=flags)
        
        return FeatureFlags.get(user)
    
    def get(user:User):
        """tries to get the feature flags

        Args:
            user (User)

        Raises:
            FeatureFlags.FeatureFlagsDoNotExistException: if the feature flags do not exist.

        Returns:
            FeatureFlag object
        """
        assert isinstance(user, User), "user argument should be an instance of User class: {}".format(type(user))
        
        if not FeatureFlags.exists(user):
            raise FeatureFlags.FeatureFlagsDoNotExistException
        
        return FeatureFlags.objects.filter(user=user).get()