from django.db import models

from adherence_messages.services import (
    AdherenceAppInstallMessageService,
    AdherenceFitbitUpdatedService
)
from fitbit_api.models import (
    FitbitAccount,
    FitbitAccountUser#,
    #FitbitSubscriptionUpdate
)
from fitbit_api.services import (
    FitbitService  #,
    # FitbitSubscriptionUpdate
)


class AdherenceAppInstallDashboard(AdherenceAppInstallMessageService):

    def __init__(self, user=None):
        self._user = user


# class AdherenceFitbitUpdatedDashboard(AdherenceFitbitUpdatedService):

#     def __init__(self, user=None):
#         self._user = user


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
        # print("Init acct: " + str(self.__account))

    def get_account(user):
        try:
            super(FitbitServiceDashboard, self).get_account()
        except FitbitServiceDashboard.NoAccount:
            return None

    def last_updated_on(self):
        try:
            super(FitbitServiceDashboard, self).last_updated_on()
            x = super(FitbitServiceDashboard, self).last_updated_on()
            print("Updated!")
            print("x: " + str(x))
            print("Date: " + str(self.last_updated_on()))
        except FitbitServiceDashboard.AccountNeverUpdated:
            return None
