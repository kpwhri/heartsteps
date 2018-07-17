import uuid
from django.db import models

from django.contrib.auth.models import User

MORNING = 'morning'
LUNCH = 'lunch'
MIDAFTERNOON = 'midafternoon'
EVENING = 'evening'
POSTDINNER = 'postdinner'

TIMES = [MORNING, LUNCH, MIDAFTERNOON, EVENING, POSTDINNER]

TIME_CATEGORIES = [
    (MORNING, 'Morning'),
    (LUNCH, 'Lunch'),
    (MIDAFTERNOON, 'Afternoon'),
    (EVENING, 'Evening'),
    (POSTDINNER, 'Post dinner')
]

class SuggestionTime(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    type = models.CharField(max_length=20, choices=TIME_CATEGORIES)
    time_of_day = models.CharField(max_length=25)

    user = models.ForeignKey(User)

    def __str__(self):
        return "%s (%s) - %s" % (self.time_of_day, self.type, self.user)