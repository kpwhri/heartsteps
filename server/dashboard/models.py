from django.db import models

from adherence_messages.services import (
    AdherenceAppInstallMessageService,
    AdherenceFitbitUpdatedService
)
from fitbit_api.models import (FitbitAccount, FitbitAccountUser)
from fitbit_api.services import FitbitService


class AdherenceAppInstallDashboard(AdherenceAppInstallMessageService):

    def __init__(self, user=None):
        self._user = user


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
