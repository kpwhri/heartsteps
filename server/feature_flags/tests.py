from django.test import TestCase
from .models import User

from feature_flags.models import FeatureFlags


# Create your tests here.
class FeatureFlagsTestCase(TestCase):
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test")

    def tearDown(self):
        """Destroying testing user"""
        self.user.delete()

    def test_create_0(self):
        """Check create function's prototype"""

        # create function shouldn't be called without argument
        self.assertRaises(TypeError, FeatureFlags.create)

        # create function's arg 1 should be User model
        self.assertRaises(AssertionError, FeatureFlags.create, 1)
        self.assertRaises(AssertionError, FeatureFlags.create, 1, "test")
        self.assertRaises(AssertionError, FeatureFlags.create, 1, 1)

        # create function's arg 2 should be a string
        self.assertRaises(AssertionError, FeatureFlags.create, self.user, 1)

    def test_create_1_1(self):
        """Check if create function works fine - without flags"""
        # create blank featureflags
        obj = FeatureFlags.create(self.user)

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "")

    def test_create_1_2(self):
        """Check if create function works fine - with flags"""
        # create "test" featureflag
        obj = FeatureFlags.create(self.user, "test")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "test")

    def test_create_2(self):
        """Check if create function's exceptions are raised correctly"""
        # create a featureFlag for the first time
        FeatureFlags.create(self.user)

        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FeatureFlags.FeatureFlagExistsException,
                          FeatureFlags.create, self.user)

    def test_exists_0(self):
        """Check exists function's prototype"""
        # create function shouldn't be called without argument
        self.assertRaises(TypeError, FeatureFlags.exists)
        # create function's arg 1 should be User model
        self.assertRaises(AssertionError, FeatureFlags.exists, 1)

    def test_exists_1(self):
        """Check if exists function works fine"""
        # check if it exists
        ret1 = FeatureFlags.exists(self.user)
        # returns false
        self.assertFalse(ret1)
        # once create it
        FeatureFlags.create(self.user)
        # returns true
        ret2 = FeatureFlags.exists(self.user)
        self.assertTrue(ret2)

    def test_update_0(self):
        """Check update()'s prototype"""
        # before we start with the update(), we need to create the flags first
        FeatureFlags.create(self.user)

        # update function shouldn't be called without argument
        self.assertRaises(TypeError, FeatureFlags.update)

        # update function shouldn't be called without argument 2
        self.assertRaises(TypeError, FeatureFlags.update, self.user)

        # update function's arg 1 should be User model
        self.assertRaises(AssertionError, FeatureFlags.update, 1, 1)
        self.assertRaises(AssertionError, FeatureFlags.update, 1, "test")
        
        # update function's arg 2 should be a string
        self.assertRaises(AssertionError, FeatureFlags.update, self.user, 1)
        
    def test_update_1(self):
        """Check if create function works fine"""
        # create "test" featureflag
        obj = FeatureFlags.create(self.user, "test")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "test")
        
        obj2 = FeatureFlags.update(self.user, "test2")
        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.flags, "test2")
        