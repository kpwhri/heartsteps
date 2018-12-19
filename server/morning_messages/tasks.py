from celery import shared_task

@shared_task
def send_morning_message(username):
    print("hello")
