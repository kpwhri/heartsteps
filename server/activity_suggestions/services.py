
from randomization.services import DecisionService, DecisionContextService, DecisionMessageService

class ActivitySuggestionService():
    """
    Handles state and requests between activity-suggestion-service and
    heartsteps-server for a specific participant.
    """

    def initialize(self):
        pass

    def update(self, date):
        pass
    
    def decide(self, decision):
        pass

class ActivitySuggestionDecisionService(DecisionContextService, DecisionMessageService):
    
    def decide(self):
        self.decision.a_it = True
        self.decision.pi_it = 1
        self.decision.save()

        return self.decision.a_it
