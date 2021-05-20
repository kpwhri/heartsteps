from heartsteps.tests import HeartStepsTestCase
from django.contrib.auth.models import User
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response

from participants.models import Participant

from generic_messages.views import GenericMessagesMessageCreateView
from generic_messages.services import GenericMessagesService
from generic_messages.models import GenericMessagesConfiguration
from uuid import UUID


class GenericMessagesTest(HeartStepsTestCase):
    # models.py
    
    # views.py
    
    def test_views_obj_create_test_1(self):
        obj = GenericMessagesMessageCreateView()
    
    def test_views_method_test_1(self):
        obj = GenericMessagesMessageCreateView()
        self.assertRaises(AssertionError, obj.post, None)

    def test_views_method_test_2(self):
        obj = GenericMessagesMessageCreateView()
        request = HttpRequest()
        self.assertRaises(AssertionError, obj.post, request)
    
    def test_views_method_test_3(self):
        obj = GenericMessagesMessageCreateView()
        request = HttpRequest()
        request.user = self.user
        self.assertRaises(GenericMessagesService.NoConfiguration, obj.post, request)
    
    

    def test_views_method_test_3(self):
        obj = GenericMessagesMessageCreateView()
        GenericMessagesConfiguration.objects.create(user=self.user, enabled=True)
        
        request = HttpRequest()
        request.user = self.user
        post_response = obj.post(request)
        
        self.checkif_non_none({
            "post_response": post_response
        })
        self.checkif_has_attr("post_response", post_response, [
            "status_code",
            "data"
        ])
        self.checkif_has_key("post_response.data", post_response.data, [
            "messageId"
        ])
        self.checkif_non_none({
            "post_response.data['messageId']": post_response.data['messageId']
        })
        