from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heartsteps.settings')

app = Celery('heartsteps')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-pooling-service': {
        'task': 'walking_suggestions.tasks.update_pooling_service',
        'schedule': crontab(hour='10', minute='0')
    },
    'reset-test-participants': {
        'task': 'participants.tests.reset_test_participants',
        'schedule': crontab(hour='11', minute='0')
    },
}

app.conf.task_default_queue = 'default'
app.conf.task_routes = {
    'participants.tasks.export_user_data': {
        'queue': 'export'
    },
    'activity_surveys.tasks.*': {
        'queue': 'messages'
    },
    'anti_sedentary.tasks.*': {
        'queue': 'messages'
    },
    'closeout_messages.tasks.*': {
        'queue': 'messages'
    },
    'heartsteps_messages.tasks.*': {
        'queue': 'messages'
    },
    'fitbit_activities.tasks.*': {
        'queue': 'fitbit'
    },
    'morning_messages.tasks.*': {
        'queue': 'messages'
    },
    'push_messages.tasks.*': {
        'queue': 'messages'
    },
    'walking_suggestion_surveys.tasks.*': {
        'queue': 'messages'
    },
    'walking_suggestions.tasks.*': {
        'queue': 'messages'
    },
    'weekly_reflection.tasks.*': {
        'queue': 'messages'
    }
}
