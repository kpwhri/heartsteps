from django.test import TestCase

from .models import Configuration
from .models import User
from .models import WalkingSuggestionSurvey

class TestBase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            username='test'
        )
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )

