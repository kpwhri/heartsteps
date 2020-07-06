from randomization.resources import DecisionResource
from walking_suggestions.models import WalkingSuggestionDecision

class WalkingSuggestionDecisionResource(DecisionResource):

    class Meta:
        model = WalkingSuggestionDecision
        fields = DecisionResource.FIELDS
        export_order = DecisionResource.FIELDS