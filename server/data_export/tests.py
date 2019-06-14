# from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

from data_export.resources import MODEL_NOT_FOUND


# class DataExportTestCase(APITestCase):
# 
    # def test_existing_table_on_step_data(self):
    #     response = self.client.get(reverse('data-export', args=['step_counts']))
    #     step_count_header = b'id,user,steps,start,end,created,updated\r\n'
    #     self.assertEqual(response.content, step_count_header)

    # def test_missing_table(self):
    #     response = self.client.get(reverse('data-export', args=['fake_table']))
    #     self.assertEqual(str(response.content), f"b'{MODEL_NOT_FOUND}'")
