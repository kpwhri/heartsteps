from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heartsteps.settings')

app = Celery('heartsteps')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# This will prevent celery's backend clean up from running
# which will make all task results persist in the database
# https://docs.celeryproject.org/en/latest/userguide/configuration.html#result-expires
app.conf.result_expires = None

# This should make celery workers only reserve a single task
# preventing message sending tasks from getting stuck behind
# longer tasks, like nightly updates.
# https://docs.celeryproject.org/en/stable/userguide/configuration.html#std-setting-worker_prefetch_multiplier
app.conf.worker_prefetch_multiplier = 1

app.conf.beat_schedule = {
    'reset-test-participants': {
        'task': 'participants.tasks.reset_test_participants',
        'schedule': crontab(hour='11', minute='0')
    },
    'export-cohort-data': {
        'task': 'participants.tasks.export_cohort_data',
        'schedule': crontab(hour='11', minute='0')
    }
}
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"

app.conf.task_default_queue = 'default'
app.conf.task_routes = {
    'participants.tasks.export_user_data': {
        'queue': 'default'
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
    'fitbit_activities.tasks.update_fitbit_data': {
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
    },
    'nlm.tasks.*': {
        'queue': 'messages'
    }
}
