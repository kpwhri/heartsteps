from django.test import TestCase

from zipcode.models import ZipCodeRequestHistory
from .models import User

# Create your tests here.

class ZipCodeModelTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create(username='testuser')

    def test_zipcode_model(self):
        ZipCodeRequestHistory.objects.create(
            zipcode='12345',
            user=self.user,
            response_code='200',
            response_message='OK',
            latitude=1.0,
            longitude=1.0,
            state='CA',
            city='San Diego',
            when_requested=None
        )
    
    