import pytz
from datetime import timedelta
from celery import shared_task

from django.utils import timezone

from anti_sedentary.services import AntiSedentaryDecisionService
from anti_sedentary.tasks import make_decision

from .models import StepCount

@shared_task
def start_decision(step_count_id):
    try:
        step_count = StepCount.objects.get(id = step_count_id)
    except StepCount.DoesNotExist:
        return False

    if step_count.step_number < 150:
        decision_service = AntiSedentaryDecisionService.create_decision(
            user = step_count.user
        )
        decision_service.decision.add_context_object(step_count)
        make_decision.apply_async(kwargs={
            'decision_id': str(decision_service.decision.id)
        })
