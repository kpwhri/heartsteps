from celery import shared_task

from .models import Configuration

@shared_task
def send_message(username):
    configuration = Configuration.objects.get(user__username = username)
    configuration.send_message()
