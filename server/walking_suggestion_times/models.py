from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from locations.services import LocationService

class SuggestionTime(models.Model):

    MORNING = 'morning'
    LUNCH = 'lunch'
    MIDAFTERNOON = 'midafternoon'
    EVENING = 'evening'
    POSTDINNER = 'postdinner'

    TIMES = [MORNING, LUNCH, MIDAFTERNOON, EVENING, POSTDINNER]

    CATEGORIES = [
        (MORNING, 'Morning'),
        (LUNCH, 'Lunch'),
        (MIDAFTERNOON, 'Afternoon'),
        (EVENING, 'Evening'),
        (POSTDINNER, 'Post dinner')
    ]

    user = models.ForeignKey(User)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    hour = models.PositiveSmallIntegerField()
    minute = models.PositiveSmallIntegerField()

    def __str__(self):
        return "%s:%s (%s) - %s" % (self.hour, self.minute, self.category, self.user)         

    def get_datetime_on(self, date):
        location_service = LocationService(self.user)
        tz = location_service.get_timezone_on(date)
        return tz.localize(datetime(
            date.year,
            date.month,
            date.day,
            self.hour,
            self.minute
        )) 
