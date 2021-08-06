from django.test import TestCase
from .models import User

from feature_flags.models import FeatureFlags

# Create your tests here.
class FeatureFlagsTestCase(TestCase):
    """Create testing user"""
    def setUp(self):
        self.user = User.objects.create(username="test")
    
    """Destroying testing user"""
    def tearDown(self):
        self.user.delete()
    
    """Check create function's prototype"""
    def test_create_0(self):
        # create function shouldn't be called without argument
        self.assertRaises(TypeError, FeatureFlags.create)

        # create function's arg 1 should be User model
        self.assertRaises(AssertionError, FeatureFlags.create, 1)
        self.assertRaises(AssertionError, FeatureFlags.create, 1, "test")
        self.assertRaises(AssertionError, FeatureFlags.create, 1, 1)

        # create function's arg 2 should be a string
        self.assertRaises(AssertionError, FeatureFlags.create, self.user, 1)
    
    """Check if create function works fine - without flags"""
    def test_create_1_1(self):
        # create blank featureflags
        obj = FeatureFlags.create(self.user)
        
        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "")
    
    """Check if create function works fine - with flags"""
    def test_create_1_2(self):
        # create "test" featureflag
        obj = FeatureFlags.create(self.user, "test")
        
        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "test")
    
    """Check if create function's exceptions are raised correctly"""
    def test_create_2(self):
        # create a featureFlag for the first time
        FeatureFlags.create(self.user)
        
        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FeatureFlags.FeatureFlagExistsError, FeatureFlags.create, self.user)
    
    """Check exists function's prototype"""
    def test_exists_0(self):
        # create function shouldn't be called without argument
        self.assertRaises(TypeError, FeatureFlags.exists)
        # create function's arg 1 should be User model
        self.assertRaises(AssertionError, FeatureFlags.exists, 1)
    
    """Check if exists function works fine"""
    def test_exists_1(self):
        # check if it exists
        ret1 = FeatureFlags.exists(self.user)
        # returns false
        self.assertFalse(ret1)
        # once create it
        FeatureFlags.create(self.user)
        # returns true
        ret2 = FeatureFlags.exists(self.user)
        self.assertTrue(ret2)