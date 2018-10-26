import requests
import json
from datetime import timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from randomization.services import DecisionService, DecisionContextService, DecisionMessageService

from .activity_suggestion_service import ActivitySuggestionService

class ActivitySuggestionDecisionService(DecisionContextService, DecisionMessageService):
    
    def decide(self):

        try:
            service = ActivitySuggestionService(self.user)
            service.decide(decision)
        except ImproperlyConfigured:
            self.decision.a_it = True
            self.decision.pi_it = 1
            self.decision.save()

        return self.decision.a_it
