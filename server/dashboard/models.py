from datetime import date
from datetime import timedelta

from django.db import models

from adherence_messages.services import (
    AdherenceAppInstallMessageService,
    AdherenceFitbitUpdatedService
)
from anti_sedentary.models import AntiSedentaryDecision
from days.services import DayService
from fitbit_api.models import (FitbitAccount, FitbitAccountUser)
from fitbit_api.services import FitbitService
from participants.models import Participant
from randomization.models import UnavailableReason
from sms_messages.models import (Contact, Message)
from walking_suggestions.models import WalkingSuggestionDecision
from watch_app.models import StepCount as WatchAppStepCount

class AdherenceAppInstallDashboard(AdherenceAppInstallMessageService):

    def __init__(self, user=None):
        self._user = user

class InterventionSummary:
    
    def __init__(
            self,
            availability,
            decisions,
            messages_sent,
            unavailable_reasons
            ):
        self.availability = availability
        self.decisions = decisions
        self.messages_sent = messages_sent
        self.unavailable_reasons = unavailable_reasons
    
class InterventionSummaryManager(models.Manager):

    def get_intervention_decisions(self, model, users, start, end):
        query = model.objects.filter(
            user__in = users,
            time__gte = start,
            time__lte = end,
            test = False
        )
        return query.all()

    def get_walking_suggestions(self, users, start, end):
        return self.get_intervention_decisions(
            model = WalkingSuggestionDecision,
            users = users,
            start = start,
            end = end
        )

    def get_anti_sedentary_decisions(self, users, start, end):
        return self.get_intervention_decisions(
            model = AntiSedentaryDecision,
            users = users,
            start = start,
            end = end
        )

    def count_unavailable_reasons(self, decisions):
        unavailable_reasons = {}
        query = UnavailableReason.objects.filter(
            decision__in = decisions
        )
        for _reason in query.all():
            if _reason.reason not in unavailable_reasons:
                unavailable_reasons[_reason.reason] = 0
            unavailable_reasons[_reason.reason] += 1
        return unavailable_reasons

    def list_unavailable_reasons(self, decisions):
        counts = self.count_unavailable_reasons(decisions)
        decisions_total = len(decisions)
        unavailable_reasons = []
        for reason, name in UnavailableReason.CHOICES:
            count = 0
            percentage = 0
            if reason in counts:
                count = counts[reason]
            if decisions_total:
                percentage = count/decisions_total
            unavailable_reasons.append({
                'name': name,
                'reason': reason,
                'count': count,
                'percentage': percentage
            })
        unavailable_reasons.sort(key = lambda x: (1-x['percentage'], x['name']))
        return unavailable_reasons

    def filter_decisions(self, start, end, decisions):
        _decisions = []
        for decision in decisions:
            if decision.time >= start and decision.time <= end:
                _decisions.append(decision)
        return _decisions

    def summarize_interventions(self, users, start, end, decisions):
        total_decisions = 0
        available_decisions = 0
        messages_sent = 0
        decisions = self.filter_decisions(start, end, decisions)
        for decision in decisions:
            total_decisions += 1
            if decision.treated:
                messages_sent += 1
            if decision.available:
                available_decisions += 1
        availability = 0
        if total_decisions:
            availability = available_decisions/total_decisions

        return InterventionSummary(
            availability = availability,
            decisions = total_decisions,
            messages_sent = messages_sent,
            unavailable_reasons = self.list_unavailable_reasons(decisions)
        )

    def summarize_anti_sedentary_suggestions(
            self,
            users,
            start,
            end,
            decisions = None
        ):
        if not decisions:
            decisions = self.get_anti_sedentary_decisions(
                users = users,
                start = start,
                end = end
            )
        return self.summarize_interventions(
            users = users,
            start = start,
            end = end,
            decisions = decisions
        )        

    def summarize_walking_suggestions(self, users, start, end, decisions=None):
        if not decisions:
            decisions = self.get_walking_suggestions(
                users = users,
                start = start,
                end = end
            )
        return self.summarize_interventions(
            users = users,
            start = start,
            end = end,
            decisions = decisions
        )

class WatchAppSummary:

    def __init__(
            self,
            seconds_available,
            total_seconds
        ):
        self.seconds_available = seconds_available
        self.total_seconds = total_seconds

    @property
    def availability(self):
        if not self.total_seconds:
            return 0
        return self.seconds_available/self.total_seconds

    @property
    def hours_available(self):
        return self.seconds_available/3600

class WatchAppSummaryManager(models.Manager):

    def get_step_counts(self, users, start, end):
        step_counts = []
        query = WatchAppStepCount.objects.filter(
            user__in = users,
            start__gte = start,
            end__lte = end
        )
        for step_count in query.all():
            if step_count.end <= step_count.created:
                step_counts.append(step_count)
        return step_counts

    def get_user_timezone(self, user, dt):
        if not self._user_timezones:
            self._user_timezones = {}
        if user.username not in self._user_timezones:
            service = DayService(user = user)


    def summary(self, users, start, end):
        seconds_available = 0
        step_counts = self.get_step_counts(users, start, end)
        for count in step_counts:
            duration = count.end - count.start
            seconds_available += duration.seconds

        difference = end - start
        total_seconds = difference.days * 24 * 60 * 60 + difference.seconds
        return WatchAppSummary(
            seconds_available = seconds_available,
            total_seconds = total_seconds
        )


class DashboardParticipant(Participant):

    summaries = InterventionSummaryManager()
    watch_app_step_counts = WatchAppSummaryManager()

    class Meta:
        proxy = True


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
