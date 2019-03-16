from datetime import datetime
import json
import pytz
from unittest.mock import patch

from django.urls import reverse

from rest_framework.test import APITestCase

from .models import PageView, User

class PageViewViewTests(APITestCase):

    def testPost(self):
        user = User.objects.create(username="test")
        self.client.force_authenticate(user=user)

        response = self.client.post(reverse('page-views'),
            json.dumps([{
                'uri': '/some/page',
                'time': '2019-03-15T14:30:02-08:00'
            }]),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)

        page_view = PageView.objects.get()
        self.assertEqual(page_view.user.username, "test")
        self.assertEqual(page_view.uri, '/some/page')
        self.assertEqual(page_view.time, datetime(2019,3,15,22,30,2).astimezone(pytz.UTC))
    
    def testMultipleObjects(self):
        user = User.objects.create(username="test")
        self.client.force_authenticate(user=user)

        response = self.client.post(reverse('page-views'),
            json.dumps([{
                'uri': '/some/page',
                'time': '2019-03-15T14:30:02-08:00'
            }, {
                'uri': '/some/other/page',
                'time': '2019-03-15T14:32:00-08:00'
            }, {
                'uri': '/some/page',
                'time': '2019-03-15T14:35:00-08:00'
            }]),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(PageView.objects.filter(user=user).count(), 3)
