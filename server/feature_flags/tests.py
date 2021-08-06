from django.test import TestCase
from .models import User
from rest_framework.test import APITestCase
from django.urls import reverse

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

        # create function's arg 1 should be User model or string username
        self.assertRaises(AssertionError, FeatureFlags.create, 1)
        self.assertRaises(AssertionError, FeatureFlags.create, 1, "test")
        self.assertRaises(AssertionError, FeatureFlags.create, 1, 1)

        # create function's arg 2 should be a string
        self.assertRaises(AssertionError, FeatureFlags.create, self.user, 1)
        self.assertRaises(AssertionError, FeatureFlags.create, self.user.username, 1)

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
        
    def test_create_1_3(self):
        """Check if create function works fine - without flags, with string username"""
        # create blank featureflags
        obj = FeatureFlags.create(self.user.username)

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "")

    def test_create_1_4(self):
        """Check if create function works fine - with flags, with string username"""
        # create "test" featureflag
        obj = FeatureFlags.create(self.user.username, "test")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "test")
        
    def test_create_1_5(self):
        """Check if create function works fine - without flags, with a wrong string username"""
        # create blank featureflags
        self.assertRaises(FeatureFlags.NoSuchUserException, FeatureFlags.create, self.user.username + "abc")

    def test_create_1_6(self):
        """Check if create function works fine - with flags, with string username"""
        # create "test" featureflag
        self.assertRaises(FeatureFlags.NoSuchUserException, FeatureFlags.create, self.user.username + "abc", "test")

    def test_create_2_1(self):
        """Check if create function's exceptions are raised correctly"""
        # create a featureFlag for the first time
        FeatureFlags.create(self.user)

        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FeatureFlags.FeatureFlagsExistException,
                          FeatureFlags.create, self.user)
    
    def test_create_2_2(self):
        """Check if create function's exceptions are raised correctly with string username: case 1"""
        # create a featureFlag for the first time
        FeatureFlags.create(self.user.username)

        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FeatureFlags.FeatureFlagsExistException,
                          FeatureFlags.create, self.user)

    def test_create_2_3(self):
        """Check if create function's exceptions are raised correctly with string username: case 2"""
        # create a featureFlag for the first time
        FeatureFlags.create(self.user)

        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FeatureFlags.FeatureFlagsExistException,
                          FeatureFlags.create, self.user.username)

    def test_create_2_4(self):
        """Check if create function's exceptions are raised correctly with string username: case 3"""
        # create a featureFlag for the first time
        FeatureFlags.create(self.user.username)

        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FeatureFlags.FeatureFlagsExistException,
                          FeatureFlags.create, self.user.username)

    def test_exists_0(self):
        """Check exists function's prototype"""
        # exists function shouldn't be called without argument
        self.assertRaises(TypeError, FeatureFlags.exists)
        # exists function's arg 1 should be User model or string username
        self.assertRaises(AssertionError, FeatureFlags.exists, 1)

    def test_exists_1_1(self):
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
        
    def test_exists_1_2(self):
        """Check if exists function works fine with string username: case 1"""
        # check if it exists
        ret1 = FeatureFlags.exists(self.user.username)
        # returns false
        self.assertFalse(ret1)
        # once create it
        FeatureFlags.create(self.user.username)
        # returns true
        ret2 = FeatureFlags.exists(self.user.username)
        self.assertTrue(ret2)
    
    def test_exists_1_3(self):
        """Check if exists function works fine with string username: case 2"""
        # check if it exists
        ret1 = FeatureFlags.exists(self.user)
        # returns false
        self.assertFalse(ret1)
        # once create it
        FeatureFlags.create(self.user.username)
        # returns true
        ret2 = FeatureFlags.exists(self.user)
        self.assertTrue(ret2)

    def test_exists_1_4(self):
        """Check if exists function works fine with string username: case 3"""
        # check if it exists
        ret1 = FeatureFlags.exists(self.user.username)
        # returns false
        self.assertFalse(ret1)
        # once create it
        FeatureFlags.create(self.user)
        # returns true
        ret2 = FeatureFlags.exists(self.user.username)
        self.assertTrue(ret2)

    def test_exists_2(self):
        """Check if exists() raises exception when username is wrong"""
        self.assertRaises(FeatureFlags.NoSuchUserException, FeatureFlags.exists, self.user.username + "abc")

    def test_update_0(self):
        """Check update()'s prototype"""
        # before we start with the update(), we need to create the flags first
        FeatureFlags.create(self.user)

        # update function shouldn't be called without argument
        self.assertRaises(TypeError, FeatureFlags.update)

        # update function shouldn't be called without argument 2
        self.assertRaises(TypeError, FeatureFlags.update, self.user)
        self.assertRaises(TypeError, FeatureFlags.update, self.user.username)

        # update function's arg 1 should be User model
        self.assertRaises(AssertionError, FeatureFlags.update, 1, 1)
        self.assertRaises(AssertionError, FeatureFlags.update, 1, "test")

        # update function's arg 2 should be a string
        self.assertRaises(AssertionError, FeatureFlags.update, self.user, 1)
        self.assertRaises(AssertionError, FeatureFlags.update, self.user.username, 1)

    def test_update_1_1(self):
        """Check if update function works fine"""
        # create "test" featureflag
        obj = FeatureFlags.create(self.user, "test")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "test")

        obj2 = FeatureFlags.update(self.user, "test2")
        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.flags, "test2")

    def test_update_1_2(self):
        """Check if update function works fine with string username"""
        # create "test" featureflag
        obj = FeatureFlags.create(self.user, "test")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "test")

        obj2 = FeatureFlags.update(self.user.username, "test2")
        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.flags, "test2")
    
    def test_update_2(self):
        """Check if update() raises right exception with wrong string username"""
        # create "test" featureflag
        obj = FeatureFlags.create(self.user, "test")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.flags, "test")

        self.assertRaises(FeatureFlags.NoSuchUserException, FeatureFlags.update, self.user.username + "abc", "test2")

    def test_get_0(self):
        """Check get()'s prototype"""
        # get() shouldn't be called without argument
        self.assertRaises(TypeError, FeatureFlags.get)
        # get()'s arg 1 should be User model
        self.assertRaises(AssertionError, FeatureFlags.get, 1)

    def test_get_1_1(self):
        """Check if get function works fine"""
        # trying to get() leads to exception if it doesn't exists
        self.assertRaises(FeatureFlags.FeatureFlagsDoNotExistException,
                          FeatureFlags.get, self.user)

        # if we create one
        obj1 = FeatureFlags.create(self.user, "test")

        self.assertEquals(obj1.user, self.user)
        self.assertEquals(obj1.flags, "test")

        # we would get the same object
        obj2 = FeatureFlags.get(self.user)

        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.flags, "test")

        # Junghwan: I don't know why but when you create a new instance, you get UUID instance for .uuid field.
        # But when you fetches it from the database, you get a UUID string.
        self.assertEquals(str(obj1.uuid), obj2.uuid)

        # if we update it
        obj3 = FeatureFlags.update(self.user, "test2")

        self.assertEquals(obj3.user, self.user)
        self.assertEquals(obj3.flags, "test2")

        self.assertEquals(str(obj1.uuid), obj3.uuid)

        # we would get the same object
        obj4 = FeatureFlags.get(self.user)

        self.assertEquals(obj4.user, self.user)
        self.assertEquals(obj4.flags, "test2")

        self.assertEquals(str(obj1.uuid), obj4.uuid)
    
    def test_get_1_2(self):
        """Check if get function works fine with string username"""
        # trying to get() leads to exception if it doesn't exists
        self.assertRaises(FeatureFlags.FeatureFlagsDoNotExistException,
                          FeatureFlags.get, self.user)
        
        self.assertRaises(FeatureFlags.FeatureFlagsDoNotExistException,
                          FeatureFlags.get, self.user.username)

        # if we create one
        obj1 = FeatureFlags.create(self.user.username, "test")

        self.assertEquals(obj1.user, self.user)
        self.assertEquals(obj1.flags, "test")

        # we would get the same object
        obj2 = FeatureFlags.get(self.user.username)

        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.flags, "test")

        # Junghwan: I don't know why but when you create a new instance, you get UUID instance for .uuid field.
        # But when you fetches it from the database, you get a UUID string.
        self.assertEquals(str(obj1.uuid), obj2.uuid)

        # if we update it
        obj3 = FeatureFlags.update(self.user.username, "test2")

        self.assertEquals(obj3.user, self.user)
        self.assertEquals(obj3.flags, "test2")

        self.assertEquals(str(obj1.uuid), obj3.uuid)

        # we would get the same object
        obj4 = FeatureFlags.get(self.user.username)

        self.assertEquals(obj4.user, self.user)
        self.assertEquals(obj4.flags, "test2")

        self.assertEquals(str(obj1.uuid), obj4.uuid)

class FeatureFlagsListViewTest(APITestCase):
    
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test_user")

    def tearDown(self):
        """Destroying testing user"""
        self.user.delete()
    
    def test_get_feature_flags_1(self):
        """get empty feature flags
        """
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)

        # get response
        response = self.client.get(reverse('feature-flags-list', kwargs={
        }))
        
        # if response code is 200
        self.assertEqual(200, response.status_code)
        # if response data is ''
        self.assertEqual(response.data['flags'], '')
        
    def test_get_feature_flags_2(self):
        # self.client.force_authenticate(user=self.user)

        # request without authentication
        response = self.client.get(reverse('feature-flags-list', kwargs={
        }))
        
        print(response.__dict__)
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['flags'], '')
        
