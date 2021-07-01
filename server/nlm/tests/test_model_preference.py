from heartsteps.tests import HeartStepsTestCase

from django.contrib.auth.models import User

from nlm.models import Preference

class ModelPreferenceTest(HeartStepsTestCase):
    def setUp(self):
        super().setUp()
        self.study_type_name = "test study type"
    
    def test_create_1(self):
        pref = Preference()
        pref.save()
        
    def test_create_2(self):
        pref, overwrite = Preference.create("test.path.value", 1)
        self.assertEqual(pref.value, 1)
        self.assertFalse(overwrite)
        pref, overwrite = Preference.create("test.path.value", "2")
        self.assertEqual(pref.value, "2")
        self.assertTrue(overwrite)
    
    def test_create_3(self):
        pref, overwrite = Preference.create("test.path.value", 3, self.user)
        self.assertEqual(pref.value,3)
        self.assertEqual(pref.user,self.user)
        self.assertFalse(overwrite)
    
    def test_delete_1(self):
        path = "test.path.value"
        pref, overwrite = Preference.create(path, 3)
        self.assertFalse(overwrite)
        pref, overwrite = Preference.create(path, 3)
        self.assertTrue(overwrite)
        Preference.delete(path)
        pref, overwrite = Preference.create(path, 3)
        self.assertFalse(overwrite)
    
        
    def test_delete_2(self):
        path = "test.path.value"
        pref, overwrite = Preference.create(path, 3, self.user)
        self.assertFalse(overwrite)
        pref, overwrite = Preference.create(path, 3, self.user)
        self.assertTrue(overwrite)
        Preference.delete(path, self.user)
        pref, overwrite = Preference.create(path, 3, self.user)
        self.assertFalse(overwrite)
    
    def test_try_to_get_1(self):
        path = "test.path.value"
        
        value, fromdb = Preference.try_to_get(path)
        self.assertEqual(value, None)
        self.assertFalse(fromdb)

        value, fromdb = Preference.try_to_get(path, default=5, convert_to_int=True)
        self.assertEqual(value, 5)
        self.assertIsInstance(value, int)
        self.assertFalse(fromdb)
        
        pref, overwrite = Preference.create(path, 4)
        self.assertFalse(overwrite)
        self.assertEqual(pref.value, 4)
        
        value, fromdb = Preference.try_to_get(path, convert_to_int=True)
        self.assertEqual(value, 4)
        self.assertIsInstance(value, int)
        self.assertTrue(fromdb)
        
        value, fromdb = Preference.try_to_get(path, default=5, convert_to_int=True)
        self.assertEqual(value, 4)
        self.assertIsInstance(value, int)
        self.assertTrue(fromdb)
        
    
    def test_try_to_get_2(self):
        path = "test.path.value"
        
        value, fromdb = Preference.try_to_get(path, self.user, convert_to_int=True)
        self.assertEqual(value, None)
        self.assertFalse(fromdb)

        value, fromdb = Preference.try_to_get(path, self.user, default=5, convert_to_int=True)
        self.assertEqual(value, 5)
        self.assertIsInstance(value, int)
        self.assertFalse(fromdb)
        
        pref, overwrite = Preference.create(path, 4, self.user)
        self.assertFalse(overwrite)
        self.assertEqual(pref.value, 4)
        
        value, fromdb = Preference.try_to_get(path, self.user, convert_to_int=True)
        self.assertEqual(value, 4)
        self.assertIsInstance(value, int)
        self.assertTrue(fromdb)
        
        value, fromdb = Preference.try_to_get(path, user=self.user, default=5, convert_to_int=True)
        self.assertEqual(value, 4)
        self.assertIsInstance(value, int)
        self.assertTrue(fromdb)