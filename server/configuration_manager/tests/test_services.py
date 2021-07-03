from django.test import TestCase

from heartsteps.tests import HeartStepsTestCase

from configuration_manager.services import ConfigurationManagerService as CMS

# Create your tests here.
class ConfigurationManagerServiceTestCase(HeartStepsTestCase):
    def test_create_service(self):
        cms = CMS(prefix='edu.ucsd.hdhl.test_study')
    
