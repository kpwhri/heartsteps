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

    class NoSuchUserException(Exception):
        pass

    class NoSuchFlagException(Exception):
        pass
    
    class Meta:
        verbose_name = 'Feature Flags'
        verbose_name_plural = 'Feature Flags'

    uuid = models.CharField(max_length=50,
                            primary_key=True,
                            default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    flags = models.TextField(default="")
        
    def __str__(self):
        return self.user.username

    def convert_to_user_obj(user):
        if isinstance(user, str):
            try:
                user_obj = User.objects.get(username=user)
            except User.DoesNotExist:
                raise FeatureFlags.NoSuchUserException
        elif isinstance(user, User):
            user_obj = user
        else:
            assert isinstance(
                user, User
            ), "user argument should be an instance of User class or a string: {}".format(
                type(user))
        return user_obj

    def create(user, flags: str = ""):
        """Create a new feature flag.
        
        Arguments: 
            user(User or str)
            flags(str) optional
        
        Raises:
            FeatureFlags.FeatureFlagsExistException : if the flag exists
            FeatureFlags.NoSuchUserException : if the username is wrong
        """
        user_obj = FeatureFlags.convert_to_user_obj(user)
        assert isinstance(flags,
                          str), "flags argument should be a string: {}".format(
                              type(flags))

        if FeatureFlags.exists(user_obj):
            raise FeatureFlags.FeatureFlagsExistException

        return FeatureFlags.objects.create(user=user_obj, flags=flags)

    def exists(user: User):
        """check if the feature flags exist

        Args:
            user (User or str)
            
        Raises:
            FeatureFlags.NoSuchUserException : if the username is wrong

        Returns:
            boolean: if the feature flags exist
        """
        user_obj = FeatureFlags.convert_to_user_obj(user)

        return FeatureFlags.objects.filter(user=user_obj).exists()

    def update(user: User, flags: str):
        """updates if the feature flags exist

        Args:
            user (User or str)
            flags (str): new feature flags

        Raises:
            FeatureFlags.FeatureFlagsDoNotExistException: if the featureFlags do not exist
            FeatureFlags.NoSuchUserException: if the user does not exist

        Returns:
            FeatureFlags object: updated feature flags
        """
        user_obj = FeatureFlags.convert_to_user_obj(user)
        assert isinstance(flags,
                          str), "flags argument should be a string: {}".format(
                              type(flags))

        if not FeatureFlags.exists(user_obj):
            raise FeatureFlags.FeatureFlagsDoNotExistException

        FeatureFlags.objects.filter(user=user_obj).update(flags=flags)

        return FeatureFlags.get(user_obj)

    def get(user: User):
        """tries to get the feature flags

        Args:
            user (User or str)

        Raises:
            FeatureFlags.FeatureFlagsDoNotExistException: if the feature flags do not exist.
            FeatureFlags.NoSuchUserException : if the username is wrong
            
        Returns:
            FeatureFlag object
        """
        user_obj = FeatureFlags.convert_to_user_obj(user)

        if not FeatureFlags.exists(user_obj):
            raise FeatureFlags.FeatureFlagsDoNotExistException

        return FeatureFlags.objects.get(user=user_obj)

    def search_users(flag: str):
        """try to get all users with a certain flag #279
        
        Args: flag (str) : flag to search
        
        Returns:
            User[] : list of users with a certain flag
        """

        assert isinstance(flag,
                          str), "flag argument should be a string: {}".format(
                              type(flag))
        assert len(flag) > 0, "flag argument should not be an empty string"
        assert flag.find(",") == -1, "flag argument should not contain a comma"

        # limits the number of users by "contain" search. It will include similar flags with suffix and prefix
        query = FeatureFlags.objects.filter(flags__contains=flag)

        user_list = []

        for feature_flags in query.all():
            if feature_flags.has_flag(flag):
                user_list.append(feature_flags.user)

        return user_list

    def has_flag(obj, flag):
        """this is weird, but intentional function polymorphism.
        You can call this as an instance method or static method.
        
        If you call this function as instance method, this will return if there's a matching flag.
        
            obj = FeatureFlags.get("username")
            print(obj.has_flag("test_flag"))
        
        If you call this function as static method, this will return if the user has a matching flag.
        
            print(FeatureFlags.has_flag("username", "test_flag"))
            print(FeatureFlags.has_flag(self.user, "test_flag"))
        """
        assert flag != "", "You can't check if an empty flag exists."
        if isinstance(obj, FeatureFlags):
            flag_list = list(map(lambda x: x.strip(), obj.flags.split(",")))

            return flag in flag_list
        elif isinstance(obj, User):
            if FeatureFlags.exists(obj):
                feature_flags = FeatureFlags.get(obj)
                return feature_flags.has_flag(flag)
            else:
                raise FeatureFlags.FeatureFlagsDoNotExistException()
        elif isinstance(obj, str):
            user_obj = FeatureFlags.convert_to_user_obj(obj)
            feature_flags = FeatureFlags.get(user_obj)
            return feature_flags.has_flag(flag)
        else:
            raise AssertionError(
                "has_flag has two prototypes: FeatureFlags.has_flag(User, str) and feature_flags.has_flag(str)"
            )

    def create_or_get(user):
        """this function only makes it easier to call create when you don't care if the feature flags of the user exist or not. 
        This keeps the original value. So it's not that dangerous.

        Returns:
            FeatureFlags: new FeatureFlag object or the old FeatureFlag object
            true: FeatureFlags object is created, false: FeatureFlags object is just retrieved
        """
        if FeatureFlags.exists(user):
            return (FeatureFlags.get(user), False)
        else:
            return (FeatureFlags.create(user), True)

    def create_or_update(user, flags):
        """This function makes it easier to call update() when you don't care if the feature flags of the user exist or not. 
        WARNING: This DOES NOT keep the original value. (It overwrite it).
                So this is dangerous!!!
        
        Returns:
            FeatureFlags: overwritten FeatureFlags object or newly-created one
            boolean: true-newly created, false-overwritten
            old_flag: if there was an existing featureflags, it will return the old flags (if newly created, None will be returned)
                """
        if FeatureFlags.exists(user):
            old_flag = FeatureFlags.get(user).flags
            return (FeatureFlags.update(user, flags), False, old_flag)
        else:
            return (FeatureFlags.create(user, flags), True, None)
        
    def add_flag(obj, flag):
        """This function adds a new flag to the flags.
        Returns:
            new object with the flag
        """
        if isinstance(obj, FeatureFlags):
            if not obj.has_flag(flag):
                obj.flags = "{}, {}".format(obj.flags, flag)
                obj.save()
            return obj
        elif isinstance(obj, User):
            if FeatureFlags.exists(obj):
                feature_flags = FeatureFlags.get(obj)
                return feature_flags.add_flag(flag)
            else:
                raise FeatureFlags.FeatureFlagsDoNotExistException()
        elif isinstance(obj, str):
            user_obj = FeatureFlags.convert_to_user_obj(obj)
            feature_flags = FeatureFlags.get(user_obj)
            return feature_flags.add_flag(flag)
        else:
            raise AssertionError(
                "add_flag has two prototypes: FeatureFlags.add_flag(User, str) and feature_flags.add_flag(str)"
            )

    def remove_flag(obj, flag):
        """This function removes an existing flag from the flags.
        Returns:
            new object without the flag
        """
        if isinstance(obj, FeatureFlags):
            if obj.has_flag(flag):
                flag_list = list(map(lambda x: x.strip(), obj.flags.split(',')))
                flag_list.remove(flag)
                obj.flags = ", ".join(flag_list)
                obj.save()
                return obj
            else:
                raise FeatureFlags.NoSuchFlagException()
        elif isinstance(obj, User):
            if FeatureFlags.exists(obj):
                feature_flags = FeatureFlags.get(obj)
                return feature_flags.remove_flag(flag)
            else:
                raise FeatureFlags.FeatureFlagsDoNotExistException()
        elif isinstance(obj, str):
            user_obj = FeatureFlags.convert_to_user_obj(obj)
            feature_flags = FeatureFlags.get(user_obj)
            return feature_flags.remove_flag(flag)
        else:
            raise AssertionError(
                "remove_flag has two prototypes: FeatureFlags.remove_flag(User, str) and feature_flags.remove_flag(str)"
            )
    
    def sort_flags(obj):
        """This function sorts flags. No actual functionality.
        Returns:
            new sorted feature flags object
        """
        if isinstance(obj, FeatureFlags):
            flag_list = list(map(lambda x: x.strip(), obj.flags.split(',')))
            obj.flags = ", ".join(sorted(flag_list, key=str.lower))
            obj.save()
            return obj
        elif isinstance(obj, User):
            if FeatureFlags.exists(obj):
                feature_flags = FeatureFlags.get(obj)
                return feature_flags.sort_flags()
            else:
                raise FeatureFlags.FeatureFlagsDoNotExistException()
        elif isinstance(obj, str):
            user_obj = FeatureFlags.convert_to_user_obj(obj)
            feature_flags = FeatureFlags.get(user_obj)
            return feature_flags.sort_flags()
        else:
            raise AssertionError(
                "remove_flag has two prototypes: FeatureFlags.sort_flags(User) and feature_flags.sort_flags()"
            )