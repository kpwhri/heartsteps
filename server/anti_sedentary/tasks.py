import pytz
from celery import shared_task

from django.utils import timezone
from django.contrib.auth import get_user_model

from anti_sedentary.services import AntiSedentaryDecisionService, AntiSedentaryService
from anti_sedentary.models import AntiSedentaryDecision

@shared_task
def start_decision(username):
    service = AntiSedentaryService(username=username)

    if service.can_randomize_now():
        decision = service.create_decision()
        make_decision.apply_async(kwargs={
            'decision_id': str(decision.id)
        })

@shared_task
def make_decision(decision_id):
    decision = AntiSedentaryDecision.objects.get(id=decision_id)
    if decision.is_complete():
        return False
    
    decision_service = AntiSedentaryDecisionService(decision)
    decision_service.update_availability()
    if decision_service.decide():
        decision_service.update_context()
        decision_service.send_message()
