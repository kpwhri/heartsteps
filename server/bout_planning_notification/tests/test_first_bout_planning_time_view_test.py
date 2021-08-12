from django.test import TestCase
from bout_planning_notification.models import User, FirstBoutPlanningTime
from rest_framework.test import APITestCase
from django.urls import reverse    


class FirstBoutPlanningTimeViewTest(APITestCase):
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test_user")
        self.url = 'first-bout-planning-time'

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
        """get 7:00 return"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)

        # get response
        response = self.client.get(reverse(self.url, kwargs={}))
        
        # if response code is 200
        self.assertEqual(200, response.status_code)
        
        # if response data is ''
        self.assertEqual(response.data['time'], '07:00')


    def test_post_0(self):
        """fail intentionally with unauthorized request(post)"""
        
        # pretend we're not authenticated

        # get response
        response = self.client.post(reverse(self.url, kwargs={}))
        
        # let's see if response code is 401 (unauthorized)
        self.assertEqual(401, response.status_code)
        
    def test_post_1(self):
        """create 8:00 and get 8:00 return"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse(self.url, kwargs={}))
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['time'], '07:00')
        
        # try to update by post
        response = self.client.post(reverse(self.url), {'time': "08:00"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['time'], '08:00')
        
        # get response
        response = self.client.get(reverse(self.url, kwargs={}))
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['time'], '08:00')


    def test_post_2(self):
        """without creating 8:00 and try to update to 8:00. see what happens"""
        
        # force authenticated as test user
        self.client.force_authenticate(user=self.user)
        
        # without creating 8:00 and try to update to 8:00. it should work as same
        response = self.client.post(reverse(self.url), {'time': "08:00"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['time'], '08:00')
        
        # get response
        response = self.client.get(reverse(self.url, kwargs={}))
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data['time'], '08:00')
