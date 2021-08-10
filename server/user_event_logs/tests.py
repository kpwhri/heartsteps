from django.test import TestCase
from .models import User, EventLog
from rest_framework.test import APITestCase
from django.urls import reverse

class EventLogTest(TestCase):
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test_user")

    def tearDown(self):
        """Destroying testing user"""
        self.user.delete()
    
    def test_log_0(self):
        # insufficient arguments
        self.assertRaises(TypeError, EventLog.log)
        self.assertRaises(TypeError, EventLog.log, self.user)
        self.assertRaises(TypeError, EventLog.log, self.user, "test msg")
        
        # user argument
        self.assertRaises(AssertionError, EventLog.log, 1, "test msg", EventLog.DEBUG)
        # user argument can be None (system log)
        EventLog.log(None, "test msg", EventLog.DEBUG)
        
        # action argument
        # if action argument is not str, it is converted to string
        EventLog.log(self.user, 1, EventLog.DEBUG)
        
        # status argument
        # the status argument should be called via EventLog.XXXX
        self.assertRaises(ValueError, EventLog.log, self.user, 1, "abc")
        
    def test_log_1(self):
        
        # generate 10 logs
        n = 10
        
        for i in range(n):
            EventLog.log(self.user, str(i), EventLog.DEBUG)
        
        # get logs
        logs = EventLog.get_logs(self.user)
        logs_msg = list(map(lambda x: x.action, logs))
        
        self.assertEqual(logs_msg, list(map(lambda x: str(x), range(n-1, -1, -1))))
        
        
        

class EventLogViewTest(APITestCase):
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
        page = 1
        pagesize = 10
        
        
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
        self.assertEqual(logs, list(map(lambda x: str(x), range(n - (page - 1) * pagesize - 1, n - page * pagesize - 1, -1))))
        
    def test_get_3(self):
        """try to make 100 logs and fetch the first page"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)


        # generate 100 logs
        n = 100
        page = 1
        pagesize = 10
        
        
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
            
        self.assertEqual(logs, list(map(lambda x: str(x), range(n - (page - 1) * pagesize - 1, n - page * pagesize - 1, -1))))
        
    
    def test_get_4(self):
        """try to make 100 logs and fetch the second page"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)


        # generate 100 logs
        n = 100
        
        page = 2
        pagesize = 10
        
        for i in range(n):
            EventLog.log(self.user, str(i), EventLog.DEBUG)
        
        # get response
        response = self.client.get(reverse(self.url, kwargs={}), {'page': page})
        
        # if response code is 200
        self.assertEqual(200, response.status_code)
        
        # if response data is ''
        logs = []
        for logline in response.data['logs']:
            logs.append(logline['action'])
            
        self.assertEqual(logs, list(map(lambda x: str(x), range(n - (page - 1) * pagesize - 1, n - page * pagesize - 1, -1))))
    
    def test_get_5(self):
        """try to make 100 logs and fetch the second page with page size of 20"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)


        # generate 100 logs
        n = 100
        page = 2
        pagesize = 20
        
        for i in range(n):
            EventLog.log(self.user, str(i), EventLog.DEBUG)
        
        # get response
        response = self.client.get(reverse(self.url, kwargs={}), {'page': page, 'pagesize': pagesize})
        
        # if response code is 200
        self.assertEqual(200, response.status_code)
        
        # if response data is ''
        logs = []
        for logline in response.data['logs']:
            logs.append(logline['action'])
            
        self.assertEqual(logs, list(map(lambda x: str(x), range(n - (page - 1) * pagesize - 1, n - page * pagesize - 1, -1))))
        
    def test_get_6(self):
        """try to make 100 logs and fetch the whole thing with page size of 15"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)


        # generate 100 logs
        n = 100
        page = 1
        pagesize = 15
        
        for i in range(n):
            EventLog.log(self.user, str(i), EventLog.DEBUG)
        
        
        logs = []
        
        condition = True
        
        while condition:
            # get response
            response = self.client.get(reverse(self.url, kwargs={}), {'page': page, 'pagesize': pagesize})
            
            # if response code is 200
            self.assertEqual(200, response.status_code)
            
            # if response data is ''
            
            for logline in response.data['logs']:
                logs.append(logline['action'])

            if page < response.data['max_page']:
                page += 1
            else:
                condition = False
        
        self.assertEqual(logs, list(map(lambda x: str(x), range(n - 1, -1, -1))))