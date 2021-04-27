from datetime import datetime
from datetime import timedelta
import pytz

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Day(models.Model):
    user = models.ForeignKey(
        User,
        related_name="+",
        on_delete = models.CASCADE
    )
    date = models.DateField()
    timezone = models.CharField(max_length=150)

    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        ordering = ['date']

    def get_timezone(self):
        return pytz.timezone(self.timezone)

    def localize(self, datetime):
        return datetime.astimezone(self.get_timezone())

    def set_start(self):
        self.start = datetime(
            self.date.year,
            self.date.month,
            self.date.day,
            tzinfo = self.get_timezone()
        )

    def set_end(self):
        self.end = datetime(
            self.date.year,
            self.date.month,
            self.date.day,
            tzinfo = self.get_timezone()
        ) + timedelta(days=1)

    def __str__(self):
        return '%s: %s' % (self.user.username, self.date.strftime('%Y-%m-%d'))

class LocalizeTimezoneQuerySet(models.QuerySet):

    def localize_results_attribute_timezone(self, attribute):
        if self._result_cache:
            self.localize_datetime(self._result_cache, attribute)
        
    def cache_timezones(self, user_ids, start, end):
        days_by_user_id = {}
        for user_id in user_ids:
            days_by_user_id[user_id] = []
        days = Day.objects.filter(
            user_id__in = user_ids,
            end__gte = start,
            start__lte = end
        ).all()
        for day in days:
            days_by_user_id[day.user_id].append(day)
        for user_id in days_by_user_id.keys():
            days_by_user_id[user_id].sort(key = lambda day: day.start)
        return days_by_user_id

    def set_timezone(self, timezone_dict, user_id, _datetime):
        if user_id in timezone_dict:
            days = timezone_dict[user_id]
            for day in days:
                if day.end > _datetime:
                    return day.localize(_datetime)
        return _datetime

    def localize_datetime(self, objects, attribute):
        datetimes_by_user_id = {}
        for _object in objects:
            _datetime = getattr(_object, attribute, None)
            _user_id = getattr(_object, 'user_id', None)
            _object_id = getattr(_object, 'id', None)
            if _object_id and _user_id and _datetime and isinstance(_datetime, datetime):
                if _user_id not in datetimes_by_user_id:
                    datetimes_by_user_id[_user_id] = {}
                datetimes_by_user_id[_user_id][_object_id] = _datetime
        queries = []
        for user_id in datetimes_by_user_id.keys():
            for decision_id, _datetime in datetimes_by_user_id[user_id].items():
                queries.append(models.Q(
                    user_id = user_id,
                    start__lte = _datetime,
                    end__gte = _datetime
                ))
        query = queries.pop()
        for item in queries:
            query |= item
        days_by_user_id = {}
        for _day in Day.objects.filter(query).all():
            if _day.user_id not in days_by_user_id:
                days_by_user_id[_day.user_id] = []
            days_by_user_id[_day.user_id].append(_day)
        for user_id in datetimes_by_user_id.keys():
            if user_id in days_by_user_id:
                days = sorted(days_by_user_id[user_id], key=lambda _day: _day.date)
                for decision_id, _datetime in datetimes_by_user_id[user_id].items():
                    _timezone = None
                    for day in days:
                        if _datetime < day.end:
                            _timezone = day.get_timezone()
                            break
                    if _timezone:
                        datetimes_by_user_id[user_id][decision_id] = _datetime.astimezone(_timezone)
        for _object in objects:
            _user_id = getattr(_object, 'user_id', None)
            _object_id = getattr(_object, 'id', None)
            if _user_id and _object_id and _user_id in datetimes_by_user_id and _object_id in datetimes_by_user_id[_user_id]:
                corrected_datetime = datetimes_by_user_id[_user_id][_object_id]
                setattr(_object, attribute, corrected_datetime)
