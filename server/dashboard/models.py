from datetime import date
from datetime import timedelta

from django.db import models

from adherence_messages.services import (
    AdherenceAppInstallMessageService,
    AdherenceFitbitUpdatedService
)
from anti_sedentary.models import AntiSedentaryDecision
from walking_suggestions.models import WalkingSuggestionDecision
from days.services import DayService
from fitbit_api.models import (FitbitAccount, FitbitAccountUser)
from fitbit_api.services import FitbitService
from participants.models import Participant
from sms_messages.models import (Contact, Message)


class AdherenceAppInstallDashboard(AdherenceAppInstallMessageService):

    def __init__(self, user=None):
        self._user = user

class TimeRange:

    def __init__(self, name, offset):
        self.name = name
        self.offset = offset

class DashboardParticipant(Participant):

    LAST_3_DAYS = TimeRange('Last 3 days', 3)
    LAST_7_DAYS = TimeRange('Last 7 days', 7)
    LAST_14_DAYS = TimeRange('Last 14 days', 14)
    TIME_RANGES = [
        LAST_3_DAYS,
        LAST_7_DAYS,
        LAST_14_DAYS
    ]

    class Meta:
        proxy = True

    def __get_time_range(self, time_range):
        if time_range not in self.TIME_RANGES:
            raise RuntimeError('time range not found')
        else:
            service = DayService(user = self.user)
            today = service.get_current_date()
            start_date = today - timedelta(days=time_range.offset)
            return [
                service.get_start_of_day(start_date),
                service.get_end_of_day(today)
            ]

    def get_randomization_decisions(self, model, time_range):
        query = model.objects.filter(
            user = self.user,
            time__range = self.__get_time_range(time_range),
            test = False
        )
        return query.all()

    def get_anti_sedentary_decisions(self, time_range):
        return self.get_randomization_decisions(AntiSedentaryDecision, time_range)

    def get_walking_suggestion_decisions(self, time_range):
        return self.get_randomization_decisions(WalkingSuggestionDecision, time_range)


class FitbitServiceDashboard(FitbitService):

    def __init__(self, user=None):
        # Need to bring in _FitbitService__account
        # Original method uses __account which resolves to the above
        try:
            super(FitbitServiceDashboard, self).__init__(user=user)
            self._FitbitService__account = self.account
        except FitbitService.NoAccount:
            self.account = None
            self._FitbitService__account = None
            self.__user = user

    def get_account(user):
        try:
            return super(FitbitServiceDashboard, self).get_account()
        except FitbitServiceDashboard.NoAccount:
            return None

    def last_updated_on(self):
        try:
            return super(FitbitServiceDashboard, self).last_updated_on()
        except FitbitServiceDashboard.AccountNeverUpdated:
            return None
