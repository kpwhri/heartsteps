from django.test import TestCase
from .models import User, EventLog
from rest_framework.test import APITestCase
from django.urls import reverse


class FirstBoutPlanningTimeViewTest(APITestCase):
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test_user")
        self.url = 'user-logs-list'

    def tearDown(self):
        """Destroying testing user"""
        self.user.delete()
    
    def test_get_0(self):
        """fail intentionally with unauthorized request(get)"""
        
        # pretend we're not authenticated

        # get response
        response = self.client.get(reverse(self.url, kwargs={}))
        
        # let's see if response code is 401 (unauthorized)
        self.assertEqual(401, response.status_code)
        
        
    def test_get_1(self):
        """get empty logs"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)

        # get response
        response = self.client.get(reverse(self.url, kwargs={}))
        
        # if response code is 200
        self.assertEqual(200, response.status_code)
        
        # if response data is ''
        self.assertEqual(response.data['logs'], [])
        
        
    def test_get_2(self):
        """get 10 logs"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)


        # generate 10 logs
        n = 10
        
        for i in range(n):
            EventLog.log(self.user, str(i), EventLog.DEBUG)
        
        # get response
        response = self.client.get(reverse(self.url, kwargs={}))
        
        # if response code is 200
        self.assertEqual(200, response.status_code)
        
        # if response data is ''
        logs = []
        for logline in response.data['logs']:
            logs.append(logline['action'])
        self.assertEqual(logs, list(map(lambda x: str(x), range(n))))
        
    def test_get_3(self):
        """try to make 100 logs and fetch the first page"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)


        # generate 100 logs
        n = 100
        
        for i in range(n):
            EventLog.log(self.user, str(i), EventLog.DEBUG)
        
        # get response
        response = self.client.get(reverse(self.url, kwargs={}))
        
        # if response code is 200
        self.assertEqual(200, response.status_code)
        
        # if response data is ''
        logs = []
        for logline in response.data['logs']:
            logs.append(logline['action'])
            
        self.assertEqual(logs, list(map(lambda x: str(x), range(10))))