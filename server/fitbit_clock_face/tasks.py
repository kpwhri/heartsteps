from celery import shared_task

from .models import ClockFaceLog
from .models import StepCount
from .models import User
from .signals import step_count_updated

@shared_task
def update_step_counts(username):
    try:
        user = User.objects.get(username = username)

        last_step_count_updated = StepCount.objects.filter(
            user = user
        ).order_by('updated').last()
        clock_face_query = ClockFaceLog.objects.filter(
            user = user
        )
        if last_step_count_updated:
            clock_face_query = clock_face_query.filter(
                updated__gte = last_step_count_updated.updated
            )

        for log in clock_face_query.all():
            last_log = log.previous_log
            if last_log:
                steps_difference = log.steps - last_log.steps
                StepCount.objects.update_or_create(
                    user = user,
                    start = last_log.time,
                    end = log.time,
                    source = StepCount.StepCountSources.SECOND,
                    defaults= {
                        'steps': steps_difference
                    }
                )
        step_count_updated.send(User, username=username)
    except User.DoesNotExist:
        pass
