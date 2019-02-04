from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from data_export.resources import MODEL_NOT_FOUND


class DataExportTestCase(TestCase):

    def test_existing_table_on_step_data(self):
        # response = self.client.get(reverse('data-export', args=['step_data']))
        # print(reverse('data-export', args=['step_data']))
        # print(response.content)
        # self.assertEqual(response.status_code, 200)
        pass

    def test_missing_table(self):
        # response = self.client.get(reverse('data-export', args=['fake_table']))
        # self.assertEqual(str(response.content), f"b'{MODEL_NOT_FOUND}'")
        pass
