from datetime import time, timedelta
from random import choice
import uuid

from django.db import models
from django.contrib.auth.models import User

from days.services import DayService
from locations.models import Location
from daily_step_goals.models import StepGoal

class Summary(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    clock_face = models.ForeignKey(
        'ClockFace',
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )
    last_log = models.ForeignKey(
        'ClockFaceLog',
        null = True,
        on_delete = models.SET_NULL,
        related_name='+'
    )
    last_step_count = models.ForeignKey(
        'StepCount',
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )
    last_location = models.ForeignKey(
        Location,
        null = True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    last_step_goal = models.ForeignKey(
        StepGoal,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

    def update(self):
        self.clock_face = self.get_active_clock_face()
        self.last_log = self.get_last_log()
        self.last_step_count = self.get_last_step_count()
        self.last_location = self.get_last_location()
        self.last_step_goal = self.get_last_step_goal()
        self.save()

    def get_active_clock_face(self):
        if not self.user:
            return None
        return ClockFace.objects.filter(user = self.user) \
        .order_by('created') \
        .last()

    def get_last_log(self):
        if not self.user:
            return None
        return ClockFaceLog.objects.filter(user = self.user) \
        .order_by('time') \
        .last()

    def get_last_step_count(self):
        if not self.user:
            return None
        return StepCount.objects.filter(
            user = self.user
        ) \
        .order_by('start') \
        .last()

    def get_last_location(self):
        if not self.user:
            return None
        return Location.objects.filter(user = self.user) \
        .order_by('time') \
        .last()

    def get_last_step_goal(self):
        if not self.user:
            return None
        return StepGoal.objects.filter(
            user = self.user
        ) \
        .order_by('start') \
        .last()

class ClockFace(models.Model):
    pin = models.CharField(
        max_length = 10,
        unique = True
    )
    token = models.CharField(
        max_length = 50,
        unique = True,
        default = uuid.uuid4
    )
    user = models.ForeignKey(
        User,
        null = True,
        on_delete = models.SET_NULL
    )

    created = models.DateTimeField(auto_now_add=True)

    @property
    def paired(self):
        if self.user_id:
            return True
        else:
            return False

    @property
    def username(self):
        if self.user:
            return self.user.username
        else:
            return None

    def get_unique_pin(self):
        pin_choices = [str(_i) for _i in [0,1,2,3,4,5,6,7,8,9]]
        pin = ''.join([choice(pin_choices) for _ in range(5)])
        exists = ClockFace.objects.filter(pin = pin).count()
        if exists:
            return self.get_unique_pin()
        else:
            return pin

    def save(self, *args, **kwargs):
        if not self.pin:
            self.pin = self.get_unique_pin()
        super().save(*args, **kwargs)


class ClockFaceLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE
    )
    steps = models.PositiveIntegerField()
    time = models.DateTimeField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['time']

    @property
    def previous_log(self):
        previous_log = ClockFaceLog.objects.filter(
            time__lt = self.time,
            user = self.user
        ) \
        .order_by('time') \
        .last()
        if not previous_log:
            return None
        service = DayService(user=self.user)
        log_date = service.get_date_at(self.time)
        previous_log_date = service.get_date_at(previous_log.time)
        if log_date == previous_log_date:
            return previous_log
        else:
            return None



class StepCount(models.Model):
    class StepCountSources(models.TextChoices):
        FIRST = 'First Watch App'
        SECOND = 'Second Watch App'

    source = models.CharField(
        choices = StepCountSources.choices,
        db_index = True,
        max_length = 150
    )

    user = models.ForeignKey(
        User,
        db_index = True,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    steps = models.PositiveSmallIntegerField()
    start = models.DateTimeField(
        db_index = True
    )
    end = models.DateTimeField(
        db_index = True
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start']

    def __str__(self):
        return "%s steps %d @ %s" % (self.source, self.steps, self.end)
