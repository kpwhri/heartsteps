from celery import shared_task

from participants.models import Participant

@shared_task
def initialize_participant(username):
    participant = Participant.objects.get(user__username = username)

@shared_task
def nightly_update(username):
    pass