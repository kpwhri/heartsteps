import pytz
from celery import shared_task

from django.contrib.auth import get_user_model

from anti_sedentary.services import AntiSedentaryDecisionService
from anti_sedentary.models import AntiSedentaryDecision

@shared_task
def start_decision(username, step_count):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    
    decision_service = AntiSedentaryDecisionService.create_decision(user)
    make_decision.apply_async(kwargs={
        'decision_id': str(decision_service.decision.id)
    })

@shared_task
def make_decision(decision_id):
    decision = AntiSedentaryDecision.objects.get(id=decision_id)
    if decision.is_complete():
        return False
    
    decision_service = AntiSedentaryDecisionService(decision)
    decision_service.update_context()

    if decision_service.decide():
        decision_service.send_message()
