import uuid
import math
from datetime import timedelta, datetime

from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model

from activity_summaries.models import Day
from days.services import DayService
from surveys.models import Survey, Question

User = get_user_model()

class WeekQuestion(Question):
    pass

class WeekSurvey(Survey):
    QUESTION_MODEL = WeekQuestion

class Week(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    number = models.IntegerField(null=True)

    start_date = models.DateField()
    end_date = models.DateField()

    goal = models.IntegerField(null=True)
    confidence = models.FloatField(null=True)

    survey = models.ForeignKey(WeekSurvey, null=True, on_delete = models.SET_NULL)
    _barrier_options = models.JSONField(null=True)
    will_barriers_continue = models.CharField(
        max_length = 50,
        choices = [
            ('yes', 'Yes'),
            ('no', 'No'),
            ('unknown', 'Unknown')
        ],
        null = True
    )

    class Meta:
        ordering = ['start_date']

    def reset(self):
        WeeklyBarrier.objects.filter(week=self).delete()
        self._barrier_options = self.get_barrier_options()
        
        self.survey.delete()
        self.survey = WeekSurvey.objects.create(
            user = self.user
        )
        self.survey.randomize_questions()
        
        self.save()
        
    def save(self, *args, **kwargs):
        if self.number is None:
            number_of_weeks = Week.objects.filter(user=self.user).count()
            self.number = number_of_weeks + 1
        if not self.goal:
            self.goal = self.get_default_goal()
        if not self.survey:
            survey = WeekSurvey.objects.create(
                user = self.user
            )
            survey.randomize_questions()
            self.survey = survey
        if not self._barrier_options:
            self._barrier_options = self.get_barrier_options()

        super().save(*args, **kwargs)

    @property
    def id(self):
        return str(self.uuid)

    @property
    def start(self):
        return self.__localize_datetime(datetime(
            year = self.start_date.year,
            month = self.start_date.month,
            day = self.start_date.day,
            hour = 0,
            minute = 0
        ))

    @property
    def end(self):
        return self.__localize_datetime(datetime(
            year = self.end_date.year,
            month = self.end_date.month,
            day = self.end_date.day,
            hour = 23,
            minute = 59
        ))

    @property
    def previous_week(self):
        if hasattr(self, '_previous_week'):
            return self._previous_week
        week = Week.objects.filter(
            user = self.user,
            end_date__lt = self.start_date
        ).last()
        if week:
            self._previous_week = week
            return week
        else:
            return None

    @property
    def next_week(self):
        if hasattr(self, '_next_week'):
            return self._next_week
        week = Week.objects.filter(
            user = self.user,
            start_date__gt = self.end_date
        ).first()
        if week:
            self._next_week = week
            return week
        else:
            return None

    @property
    def barriers(self):
        barriers = []
        for barrier in WeeklyBarrier.objects.filter(week = self).all():
            barriers.append(barrier.barrier.name)
        barriers.sort()
        return barriers
    
    def add_barrier(self, barrier_name):
        try:
            barrier = WeeklyBarrierOption.objects.filter(
                name = barrier_name,
            ).filter(
                Q(user=None) | Q(user=self.user)
            ).get()
        except WeeklyBarrierOption.DoesNotExist:
            barrier = WeeklyBarrierOption.objects.create(
                name = barrier_name,
                user = self.user
            )
        WeeklyBarrier.objects.update_or_create(
            week = self,
            barrier = barrier
        )

    def set_barriers(self, barrier_names):
        current_barriers = self.barriers
        for barrier in self.barriers:
            if barrier not in barrier_names:
                WeeklyBarrier.objects.filter(week=self, barrier__name=barrier).delete()
        for barrier in barrier_names:
            if barrier not in current_barriers:
                self.add_barrier(barrier)

    @property
    def barrier_options(self):
        if not self._barrier_options:
            return []
        return self._barrier_options

    def _get_all_barrier_options(self):
        barrier_options = WeeklyBarrierOption.objects.filter(Q(user = None) | Q(user = self.user)).all()
        options = []
        for option in barrier_options:
            options.append(option.name)
        options.sort()
        return options

    def _get_barrier_usage_dictionay(self):
        barriers = {}
        for weekly_barrier in WeeklyBarrier.objects.filter(week__user = self.user).all():
            barrier = weekly_barrier.barrier.name
            if barrier not in barriers:
                barriers[barrier] = 0
            barriers[barrier] += 1
        for option in self._get_all_barrier_options():
            if option not in barriers:
                barriers[option] = 0
        return barriers

    def _get_previous_barriers(self):
        barriers = []
        if self.previous_week:
            for recent_barrier in WeeklyBarrier.objects.filter(week = self.previous_week).all():
                barriers.append(recent_barrier.barrier.name)
        return barriers

    def get_barrier_options(self):
        options = self._get_all_barrier_options()
        barrier_usage = self._get_barrier_usage_dictionay()
        recent_barriers = self._get_previous_barriers()
        
        options.sort(key = lambda name: barrier_usage[name], reverse=True)
        options.sort(key = lambda name: name in recent_barriers, reverse=True)
        return options

    def __localize_datetime(self, time):
        service = DayService(user=self.user)
        tz = service.get_current_timezone()
        return tz.localize(time)

    def get_default_goal(self):
        days_in_previous_week = Day.objects.filter(
            user = self.user,
            date__range = [
                self.start_date - timedelta(days=7),
                self.start_date - timedelta(days=1)
            ]
        ).all()

        total_minutes = 0
        for day in days_in_previous_week:
            total_minutes += day.total_minutes
        if total_minutes > 0:
            total_minutes += 20
        else:
            total_minutes = 90

        rounded_minutes = int(5 * math.floor(float(total_minutes)/5))

        if rounded_minutes > 150:
            rounded_minutes = 150
        return rounded_minutes

    def __str__(self):
        return "%s to %s (%s)" % (self.start_date, self.end_date, self.user)

class WeeklyBarrierOption(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey(
        User,
        null = True,
        related_name = '+',
        on_delete = models.CASCADE
    )

class WeeklyBarrier(models.Model):
    week = models.ForeignKey(
        Week,
        related_name = 'weekly_barriers_set',
        on_delete = models.CASCADE
    )
    barrier = models.ForeignKey(
        WeeklyBarrierOption,
        related_name = '+',
        on_delete = models.CASCADE
    )
