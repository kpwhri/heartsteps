from django.test import TestCase
from bout_planning_notification.models import User, FirstBoutPlanningTime
from rest_framework.test import APITestCase
from django.urls import reverse

class FirstBoutPlanningTimeModelTest(TestCase):
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test")

    def tearDown(self):
        """Destroying testing user"""
        self.user.delete()

    def test_exists_0(self):
        """Check exists function's prototype"""
        # exists function shouldn't be called without argument
        self.assertRaises(TypeError, FirstBoutPlanningTime.exists)
        # exists function's arg 1 should be User model or string username
        self.assertRaises(AssertionError, FirstBoutPlanningTime.exists, 1)

    def test_exists_1_1(self):
        """Check if exists function works fine"""
        # check if it exists
        ret1 = FirstBoutPlanningTime.exists(self.user)
        # returns false
        self.assertFalse(ret1)
        # once create it
        FirstBoutPlanningTime.create(self.user)
        # returns true
        ret2 = FirstBoutPlanningTime.exists(self.user)
        self.assertTrue(ret2)
        
    def test_exists_1_2(self):
        """Check if exists function works fine with string username: case 1"""
        # check if it exists
        ret1 = FirstBoutPlanningTime.exists(self.user.username)
        # returns false
        self.assertFalse(ret1)
        # once create it
        FirstBoutPlanningTime.create(self.user.username)
        # returns true
        ret2 = FirstBoutPlanningTime.exists(self.user.username)
        self.assertTrue(ret2)
    
    def test_exists_1_3(self):
        """Check if exists function works fine with string username: case 2"""
        # check if it exists
        ret1 = FirstBoutPlanningTime.exists(self.user)
        # returns false
        self.assertFalse(ret1)
        # once create it
        FirstBoutPlanningTime.create(self.user.username)
        # returns true
        ret2 = FirstBoutPlanningTime.exists(self.user)
        self.assertTrue(ret2)

    def test_exists_1_4(self):
        """Check if exists function works fine with string username: case 3"""
        # check if it exists
        ret1 = FirstBoutPlanningTime.exists(self.user.username)
        # returns false
        self.assertFalse(ret1)
        # once create it
        FirstBoutPlanningTime.create(self.user)
        # returns true
        ret2 = FirstBoutPlanningTime.exists(self.user.username)
        self.assertTrue(ret2)

    def test_exists_2(self):
        """Check if exists() raises exception when username is wrong"""
        self.assertRaises(FirstBoutPlanningTime.NoSuchUserException, FirstBoutPlanningTime.exists, self.user.username + "abc")


    def test_create_0(self):
        """Check create function's prototype"""

        # create function shouldn't be called without argument
        self.assertRaises(TypeError, FirstBoutPlanningTime.create)

        # create function's arg 1 should be User model or string username
        self.assertRaises(AssertionError, FirstBoutPlanningTime.create, 1)
        self.assertRaises(AssertionError, FirstBoutPlanningTime.create, 1, "test")
        self.assertRaises(AssertionError, FirstBoutPlanningTime.create, 1, 1)

        # create function's arg 2 should be a properly typed string
        self.assertRaises(AssertionError, FirstBoutPlanningTime.create, self.user, 1)
        self.assertRaises(AssertionError, FirstBoutPlanningTime.create, self.user.username, 1)
        self.assertRaises(AssertionError, FirstBoutPlanningTime.create, self.user.username, "1234")

    def test_create_1_1(self):
        """Check if create function works fine - without time string"""
        # create default(07:00) time string
        obj = FirstBoutPlanningTime.create(self.user)

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.time, "07:00")
        self.assertEquals(obj.hour, 7)
        self.assertEquals(obj.minute, 0)
        
    def test_create_1_2(self):
        """Check if create function works fine - with time string"""
        # create "08:00" time string
        obj = FirstBoutPlanningTime.create(self.user, "08:00")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.time, "08:00")
        self.assertEquals(obj.hour, 8)
        self.assertEquals(obj.minute, 0)
        
    def test_create_1_3(self):
        """Check if create function works fine - without flags, with string username"""
        # create default(07:00) time string
        obj = FirstBoutPlanningTime.create(self.user.username)

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.time, "07:00")
        self.assertEquals(obj.hour, 7)
        self.assertEquals(obj.minute, 0)
        
    def test_create_1_4(self):
        """Check if create function works fine - with flags, with string username"""
        # create "08:00" time string
        obj = FirstBoutPlanningTime.create(self.user.username, "08:00")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.time, "08:00")
        self.assertEquals(obj.hour, 8)
        self.assertEquals(obj.minute, 0)
        
    def test_create_1_5(self):
        """Check if create function works fine - without time string, with a wrong string username"""
        # create default("07:00") time string
        self.assertRaises(FirstBoutPlanningTime.NoSuchUserException, FirstBoutPlanningTime.create, self.user.username + "abc")

    def test_create_1_6(self):
        """Check if create function works fine - with time string, with string username"""
        # create "08:00" featureflag
        self.assertRaises(FirstBoutPlanningTime.NoSuchUserException, FirstBoutPlanningTime.create, self.user.username + "abc", "test")

    def test_create_2_1(self):
        """Check if create function's exceptions are raised correctly"""
        # create a featureFlag for the first time
        FirstBoutPlanningTime.create(self.user)

        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FirstBoutPlanningTime.FirstBoutPlanningTimeExistException,
                          FirstBoutPlanningTime.create, self.user)
    
    def test_create_2_2(self):
        """Check if create function's exceptions are raised correctly with string username: case 1"""
        # create a featureFlag for the first time
        FirstBoutPlanningTime.create(self.user.username)

        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FirstBoutPlanningTime.FirstBoutPlanningTimeExistException,
                          FirstBoutPlanningTime.create, self.user)

    def test_create_2_3(self):
        """Check if create function's exceptions are raised correctly with string username: case 2"""
        # create a featureFlag for the first time
        FirstBoutPlanningTime.create(self.user)

        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FirstBoutPlanningTime.FirstBoutPlanningTimeExistException,
                          FirstBoutPlanningTime.create, self.user.username)

    def test_create_2_4(self):
        """Check if create function's exceptions are raised correctly with string username: case 3"""
        # create a featureFlag for the first time
        FirstBoutPlanningTime.create(self.user.username)

        # if we create again, FeatureFlagExistsError is raised
        self.assertRaises(FirstBoutPlanningTime.FirstBoutPlanningTimeExistException,
                          FirstBoutPlanningTime.create, self.user.username)


    def test_update_0(self):
        """Check update()'s prototype"""
        # before we start with the update(), we need to create the first bout planning time first
        FirstBoutPlanningTime.create(self.user)

        # update function shouldn't be called without argument
        self.assertRaises(TypeError, FirstBoutPlanningTime.update)

        # update function shouldn't be called without argument 2
        self.assertRaises(TypeError, FirstBoutPlanningTime.update, self.user)
        self.assertRaises(TypeError, FirstBoutPlanningTime.update, self.user.username)

        # update function's arg 1 should be User model
        self.assertRaises(AssertionError, FirstBoutPlanningTime.update, 1, 1)
        self.assertRaises(AssertionError, FirstBoutPlanningTime.update, 1, "test")

        # update function's arg 2 should be a string
        self.assertRaises(AssertionError, FirstBoutPlanningTime.update, self.user, 1)
        self.assertRaises(AssertionError, FirstBoutPlanningTime.update, self.user.username, 1)

    def test_update_1_1(self):
        """Check if update function works fine"""
        # create "08:00" time string
        obj = FirstBoutPlanningTime.create(self.user, "08:00")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.time, "08:00")
        self.assertEquals(obj.hour, 8)
        self.assertEquals(obj.minute, 0)

        obj2 = FirstBoutPlanningTime.update(self.user, "09:00")
        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.time, "09:00")
        self.assertEquals(obj2.hour, 9)
        self.assertEquals(obj2.minute, 0)
        
    def test_update_1_2(self):
        """Check if update function works fine"""
        # create "08:00" time string
        obj = FirstBoutPlanningTime.create(self.user, "08:00")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.time, "08:00")
        self.assertEquals(obj.hour, 8)
        self.assertEquals(obj.minute, 0)

        obj2 = FirstBoutPlanningTime.update(self.user.username, "09:00")
        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.time, "09:00")
        self.assertEquals(obj2.hour, 9)
        self.assertEquals(obj2.minute, 0)

    def test_update_1_3(self):
        """Check if update function works fine"""
        # create "08:00" time string
        obj = FirstBoutPlanningTime.create(self.user.username, "08:00")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.time, "08:00")
        self.assertEquals(obj.hour, 8)
        self.assertEquals(obj.minute, 0)

        obj2 = FirstBoutPlanningTime.update(self.user.username, "09:00")
        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.time, "09:00")
        self.assertEquals(obj2.hour, 9)
        self.assertEquals(obj2.minute, 0)
    
    def test_update_1_4(self):
        """Check if update function works fine"""
        # create "08:00" time string
        obj = FirstBoutPlanningTime.create(self.user.username, "08:00")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.time, "08:00")
        self.assertEquals(obj.hour, 8)
        self.assertEquals(obj.minute, 0)

        obj2 = FirstBoutPlanningTime.update(self.user, "09:00")
        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.time, "09:00")
        self.assertEquals(obj2.hour, 9)
        self.assertEquals(obj2.minute, 0)
    
    def test_update_2(self):
        """Check if update() raises right exception with wrong string username"""
        # create "test" featureflag
        obj = FirstBoutPlanningTime.create(self.user, "08:00")

        self.assertEquals(obj.user, self.user)
        self.assertEquals(obj.time, "08:00")
        self.assertEquals(obj.hour, 8)
        self.assertEquals(obj.minute, 0)

        self.assertRaises(FirstBoutPlanningTime.NoSuchUserException, FirstBoutPlanningTime.update, self.user.username + "abc", "08:00")

    def test_get_0(self):
        """Check get()'s prototype"""
        # get() shouldn't be called without argument
        self.assertRaises(TypeError, FirstBoutPlanningTime.get)
        # get()'s arg 1 should be User model
        self.assertRaises(AssertionError, FirstBoutPlanningTime.get, 1)

    def test_get_1_1(self):
        """Check if get function works fine"""
        # trying to get() leads to exception if it doesn't exists
        self.assertRaises(FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException,
                          FirstBoutPlanningTime.get, self.user)

        # if we create one
        obj1 = FirstBoutPlanningTime.create(self.user, "08:00")

        self.assertEquals(obj1.user, self.user)
        self.assertEquals(obj1.time, "08:00")
        self.assertEquals(obj1.hour, 8)
        self.assertEquals(obj1.minute, 0)

        # we would get the same object
        obj2 = FirstBoutPlanningTime.get(self.user)

        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.time, "08:00")
        self.assertEquals(obj2.hour, 8)
        self.assertEquals(obj2.minute, 0)

        # Junghwan: I don't know why but when you create a new instance, you get UUID instance for .id field.
        # But when you fetches it from the database, you get a UUID string.
        self.assertEquals(obj1.id, obj2.id)

        # if we update it
        obj3 = FirstBoutPlanningTime.update(self.user, "09:00")

        self.assertEquals(obj3.user, self.user)
        self.assertEquals(obj3.time, "09:00")
        self.assertEquals(obj3.hour, 9)
        self.assertEquals(obj3.minute, 0)

        self.assertEquals(obj1.id, obj3.id)

        # we would get the same object
        obj4 = FirstBoutPlanningTime.get(self.user)

        self.assertEquals(obj4.user, self.user)
        self.assertEquals(obj4.time, "09:00")
        self.assertEquals(obj4.hour, 9)
        self.assertEquals(obj4.minute, 0)

        self.assertEquals(obj1.id, obj4.id)
    
    def test_get_1_2(self):
        """Check if get function works fine with string username"""
        # trying to get() leads to exception if it doesn't exists
        self.assertRaises(FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException,
                          FirstBoutPlanningTime.get, self.user)
        
        self.assertRaises(FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException,
                          FirstBoutPlanningTime.get, self.user.username)
        
        # if we create one
        obj1 = FirstBoutPlanningTime.create(self.user.username, "08:00")

        self.assertEquals(obj1.user, self.user)
        self.assertEquals(obj1.time, "08:00")
        self.assertEquals(obj1.hour, 8)
        self.assertEquals(obj1.minute, 0)

        # we would get the same object
        obj2 = FirstBoutPlanningTime.get(self.user.username)

        self.assertEquals(obj2.user, self.user)
        self.assertEquals(obj2.time, "08:00")
        self.assertEquals(obj2.hour, 8)
        self.assertEquals(obj2.minute, 0)

        # Junghwan: I don't know why but when you create a new instance, you get UUID instance for .id field.
        # But when you fetches it from the database, you get a UUID string.
        self.assertEquals(obj1.id, obj2.id)

        # if we update it
        obj3 = FirstBoutPlanningTime.update(self.user.username, "09:00")

        self.assertEquals(obj3.user, self.user)
        self.assertEquals(obj3.time, "09:00")
        self.assertEquals(obj3.hour, 9)
        self.assertEquals(obj3.minute, 0)

        self.assertEquals(obj1.id, obj3.id)

        # we would get the same object
        obj4 = FirstBoutPlanningTime.get(self.user.username)

        self.assertEquals(obj4.user, self.user)
        self.assertEquals(obj4.time, "09:00")
        self.assertEquals(obj4.hour, 9)
        self.assertEquals(obj4.minute, 0)

        self.assertEquals(obj1.id, obj4.id)

    def test_create_daily_task_1(self):
        # The following statement will create a FirstBoutPlanningTime as 8:00.
        # This means, 4 Daily Tasks will be created at 8am, 11am, 2pm, and 5pm
        FirstBoutPlanningTime.create(self.user, time="08:00")
        
        daily_task_list = FirstBoutPlanningTime.get_daily_tasks(self.user)
        
        self.assertEquals(len(daily_task_list), 6)
        
        start_hour = 8
        time_list = ["{:02}:00".format(start_hour+x*3) for x in range(0, 5)]
        time_list.append("{:02}:{}".format(start_hour-1, 45))
        for i in range(0, len(daily_task_list)):
            self.assertIn(daily_task_list[i].time, time_list)

    def test_create_daily_task_2(self):
        # The following statement will create a FirstBoutPlanningTime as 8:00.
        # This means, 4 Daily Tasks will be created at 8am, 11am, 2pm, and 5pm
        FirstBoutPlanningTime.create(self.user, time="08:00")
        
        # Then, change the first_bout_planning_time to 09:00.
        # This means, existing 4 Daily Tasks will be deleted, and it will create new daily tasks at 9am, 12am, 3pm, and 6pm
        FirstBoutPlanningTime.update(self.user, time="09:00")
        
        daily_task_list = FirstBoutPlanningTime.get_daily_tasks(self.user)
        
        start_hour = 9
        time_list = ["{:02}:00".format(start_hour+x*3) for x in range(0, 5)]
        time_list.append("{:02}:{}".format(start_hour-1, 45))
        
        for i in range(0, len(daily_task_list)):
            self.assertIn(daily_task_list[i].time, time_list)