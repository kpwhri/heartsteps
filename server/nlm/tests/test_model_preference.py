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
    
    # def test_create_3(self):
    #     pref = Preference.create("test.path.value", 1)
        
        
    
    # def test_try_to_get(self):
        