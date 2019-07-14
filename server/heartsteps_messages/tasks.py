from celery import shared_task

from anti_sedentary.services import AntiSedentaryDecisionService
from walking_suggestions.services import WalkingSuggestionDecisionService

@shared_task
def step_count_message_randomization(username):
    try:
        WalkingSuggestionDecisionService.make_decision_now(
            username = username
        )
    except WalkingSuggestionDecisionService.RandomizationUnavailable:
        pass
    try:
        AntiSedentaryDecisionService.make_decision_now(
            username = username
        )
    except AntiSedentaryDecisionService.RandomizationUnavailable:
        pass

