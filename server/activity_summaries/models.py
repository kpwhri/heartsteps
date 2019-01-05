from django.db import models
from django.contrib.auth import get_user_model

from fitbit_api.models import FitbitAccountUser, FitbitDay, FitbitActivity

User = get_user_model()

class Day(models.Model):

    user = models.ForeignKey(User)
    date = models.DateField()
    steps = models.PositiveIntegerField(default=0)
    miles = models.FloatField(default=0)

    moderate_minutes = models.PositiveIntegerField(default=0)
    vigorous_minutes = models.PositiveIntegerField(default=0)

    @property
    def total_minutes(self):
        return self.moderate_minutes + self.vigorous_minutes*2

    def get_fitbit_account(self):
        account_user = FitbitAccountUser.objects.get(user=self.user)
        return account_user.account

    def update_from_fitbit(self):
        try:
            fitbit_day = FitbitDay.objects.get(
                account = self.get_fitbit_account(),
                date__year = date.year,
                date__month = date.month,
                date__day = date.day
            )
            self.steps = fitbit_day.step_count
            self.miles = fitbit_day.distance
            self.save()
        except (FitbitAccountUser.DoesNotExist, FitbitDay.DoesNotExist):
            pass
    
    def update_from_activities(self):
        pass
