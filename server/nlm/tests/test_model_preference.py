from heartsteps.tests import HeartStepsTestCase

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
        pref, overwrite = Preference.create("test.path.value", 3, self.participant)
        self.assertEqual(pref.value,3)
        self.assertEqual(pref.participant,self.participant)
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
        pref, overwrite = Preference.create(path, 3, self.participant)
        self.assertFalse(overwrite)
        pref, overwrite = Preference.create(path, 3, self.participant)
        self.assertTrue(overwrite)
        Preference.delete(path, self.participant)
        pref, overwrite = Preference.create(path, 3, self.participant)
        self.assertFalse(overwrite)
        
        
        
    
    # def test_try_to_get(self):
        