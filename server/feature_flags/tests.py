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
        
    def test_search_users_0(self):
        """Check search_users()'s prototype"""
        # search_users() shouldn't be called without argument
        self.assertRaises(TypeError, FeatureFlags.search_users)
        # search_users()'s arg 1 should be a string
        self.assertRaises(AssertionError, FeatureFlags.search_users, 1)
        # search_users()'s arg 1 shouldn't be an empty string
        self.assertRaises(AssertionError, FeatureFlags.search_users, "")
        
    def test_search_users_1(self):
        """Check if search_users() is working well"""
        
        for i in range(5):
            user = User.objects.create(username="testuser_{}".format(i))
            if i in range(2,5):
                # user 2,3,4
                FeatureFlags.create(user, "flag ,flag1")
            else:
                # user 0,1
                FeatureFlags.create(user, "flag2, flag")
        
        user_list = FeatureFlags.search_users("flag1")        
        user_list_str = list(map(lambda x: x.username, user_list))
        
        for i in range(2):
            self.assertNotIn("testuser_{}".format(i), user_list_str)
        for i in range(2,5):
            self.assertIn("testuser_{}".format(i), user_list_str)
            
        user_list2 = FeatureFlags.search_users("flag")        
        user_list_str2 = list(map(lambda x: x.username, user_list2))
        
        for i in range(5):
            self.assertIn("testuser_{}".format(i), user_list_str2)
    
    def test_has_flag_0(self):
        self.assertRaises(TypeError, FeatureFlags.has_flag)
        self.assertRaises(TypeError, FeatureFlags.has_flag, 1)
        self.assertRaises(TypeError, FeatureFlags.has_flag, 1)
        self.assertRaises(TypeError, FeatureFlags.has_flag, "x")
        self.assertRaises(AssertionError, FeatureFlags.has_flag, self.user, "")
    
    def test_has_flag_1(self):
        self.assertRaises(FeatureFlags.FeatureFlagsDoNotExistException, FeatureFlags.has_flag, self.user, "test")
        obj = FeatureFlags.create(self.user, "test1, test2,test3,test4")
        self.assertEqual(obj.has_flag("test1"), True)
        self.assertEqual(obj.has_flag("test2"), True)
        self.assertEqual(obj.has_flag("test3"), True)
        self.assertEqual(obj.has_flag("test4"), True)
        self.assertEqual(obj.has_flag("test5"), False)
        
        self.assertEqual(FeatureFlags.has_flag(self.user, "test1"), True)
        self.assertEqual(FeatureFlags.has_flag(self.user, "test2"), True)
        self.assertEqual(FeatureFlags.has_flag(self.user, "test3"), True)
        self.assertEqual(FeatureFlags.has_flag(self.user, "test4"), True)
        self.assertEqual(FeatureFlags.has_flag(self.user, "test5"), False)
        
        self.assertEqual(FeatureFlags.has_flag(self.user.username, "test1"), True)
        self.assertEqual(FeatureFlags.has_flag(self.user.username, "test2"), True)
        self.assertEqual(FeatureFlags.has_flag(self.user.username, "test3"), True)
        self.assertEqual(FeatureFlags.has_flag(self.user.username, "test4"), True)
        self.assertEqual(FeatureFlags.has_flag(self.user.username, "test5"), False)
        
    def test_create_or_get_0(self):
        self.assertRaises(TypeError, FeatureFlags.create_or_get)
        self.assertRaises(AssertionError, FeatureFlags.create_or_get, 1)
        self.assertRaises(FeatureFlags.NoSuchUserException, FeatureFlags.create_or_get, "x")
    
    def test_create_or_get_1(self):
        self.assertFalse(FeatureFlags.exists(self.user))
        
        # if you didn't have a FeatureFlags object, it will create a FeatureFlags object and the boolean will be true
        obj1, boolean1 = FeatureFlags.create_or_get(self.user)
        self.assertEqual(obj1.flags, "")
        self.assertTrue(boolean1)
        
        self.assertTrue(FeatureFlags.exists(self.user))
        
        # if you have a FeatureFlags object, it will get the FeatureFlags object and the boolean will be false
        obj2, boolean2 = FeatureFlags.create_or_get(self.user)
        self.assertEqual(obj2.flags, "")
        self.assertFalse(boolean2)
        
        # if you update the feature flag,
        FeatureFlags.update(self.user, "abc")
        
        # it will get the updated FeatureFlags object and the boolean will be false
        obj3, boolean3 = FeatureFlags.create_or_get(self.user)
        self.assertEqual(obj3.flags, "abc")
        self.assertFalse(boolean3)
        
    def test_create_or_update_0(self):
        self.assertRaises(TypeError, FeatureFlags.create_or_update)
        self.assertRaises(TypeError, FeatureFlags.create_or_update, 1)
        self.assertRaises(TypeError, FeatureFlags.create_or_update, "x")
        self.assertRaises(TypeError, FeatureFlags.create_or_update, self.user)
        self.assertRaises(AssertionError, FeatureFlags.create_or_update, 1, "x")
        self.assertRaises(AssertionError, FeatureFlags.create_or_update, self.user, 1)
        self.assertRaises(FeatureFlags.NoSuchUserException, FeatureFlags.create_or_update, self.user.username + "abc", "abc")
    
    def test_create_or_update_1(self):
        self.assertFalse(FeatureFlags.exists(self.user))
        
        # if you didn't have a FeatureFlags object, it will create a FeatureFlags object and the boolean will be true
        obj1, boolean1, old_value1 = FeatureFlags.create_or_update(self.user, "test")
        self.assertEqual(obj1.flags, "test")
        self.assertTrue(boolean1)
        self.assertIsNone(old_value1)
        
        self.assertTrue(FeatureFlags.exists(self.user))
        
        # if you have a FeatureFlags object, it will get the FeatureFlags object and the boolean will be false
        obj2, boolean2, old_value2 = FeatureFlags.create_or_update(self.user, "test2")
        self.assertEqual(obj2.flags, "test2")
        self.assertFalse(boolean2)
        self.assertEqual(old_value2, "test")
        # but the uuid will be the same
        self.assertEqual(str(obj1.uuid), str(obj2.uuid))
        
    def test_add_flag_0(self):
        """prototype check"""
        self.assertRaises(TypeError, FeatureFlags.add_flag)
        
        feature_flags = FeatureFlags.create(self.user)
        self.assertRaises(TypeError, feature_flags.add_flag)
        
    def test_add_flag_1(self):
        # it will raise an exception if you call it before the creation of feature flags
        self.assertRaises(FeatureFlags.FeatureFlagsDoNotExistException, FeatureFlags.add_flag, self.user, "test")
        
        FeatureFlags.create(self.user, "test1")
        new_obj = FeatureFlags.add_flag(self.user, "test2")
        
        self.assertTrue(new_obj.has_flag("test1"))
        self.assertTrue(new_obj.has_flag("test2"))
        self.assertTrue(FeatureFlags.has_flag(self.user, "test1"))
        self.assertTrue(FeatureFlags.has_flag(self.user, "test2"))
    
    def test_remove_flag_0(self):
        """prototype check"""
        self.assertRaises(TypeError, FeatureFlags.remove_flag)
        
        feature_flags = FeatureFlags.create(self.user)
        self.assertRaises(TypeError, feature_flags.remove_flag)
        
    def test_remove_flag_1(self):
        """functionality check"""
        
        # it will raise an exception if you call it before the creation of feature flags
        self.assertRaises(FeatureFlags.FeatureFlagsDoNotExistException, FeatureFlags.remove_flag, self.user, "test")
        
        FeatureFlags.create(self.user, "test1, test2")
        new_obj = FeatureFlags.remove_flag(self.user, "test2")
        
        self.assertTrue(new_obj.has_flag("test1"))
        self.assertFalse(new_obj.has_flag("test2"))
        
        self.assertRaises(FeatureFlags.NoSuchFlagException, new_obj.remove_flag, "test2")
        self.assertRaises(FeatureFlags.NoSuchFlagException, new_obj.remove_flag, "test3")
        
        
class FeatureFlagsListViewTest(APITestCase):
    
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test_user")

    def tearDown(self):
        """Destroying testing user"""
        self.user.delete()
    
    def test_get_feature_flags_1(self):
        """get empty feature flags if we don't create feature flags before
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
        """try to get feature flags without authentication
        """
        # self.client.force_authenticate(user=self.user)

        # request without authentication
        response = self.client.get(reverse('feature-flags-list', kwargs={
        }))
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['flags'], '')
        
        response = self.client.get(reverse('feature-flags-list', kwargs={
        }))
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['flags'], '')

    def test_get_feature_flags_3(self):
        """get empty feature flags by creating an empty feature flag
        """
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)

        # create feature flags
        FeatureFlags.create(self.user)
        # get response
        response = self.client.get(reverse('feature-flags-list', kwargs={
        }))
        
        # if response code is 200
        self.assertEqual(200, response.status_code)
        # if response data is ''
        self.assertEqual(response.data['flags'], "")
                
    def test_get_feature_flags_4(self):
        """get a specific feature flags if we make that feature flags previously
        """
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)

        # create feature flags
        FeatureFlags.create(self.user, "test1, test2")
        # get response
        response = self.client.get(reverse('feature-flags-list', kwargs={
        }))
        
        # if response code is 200
        self.assertEqual(200, response.status_code)
        # if response data is ''
        self.assertEqual(response.data['flags'], "test1, test2")
    
    # TODO: make post test cases