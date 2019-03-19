from celery import shared_task

from .models import User
from .signals import weekly_reflection

@shared_task
def send_reflection(username):
    weekly_reflection.send(User, username=username)
