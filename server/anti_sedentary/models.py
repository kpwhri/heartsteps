from django.db import models
from django.contrib.auth import get_user_model

from behavioral_messages.models import MessageTemplate
from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccountUser
from randomization.models import Decision
from randomization.models import DecisionContextQuerySet
from service_requests.models import ServiceRequest

User = get_user_model()

class ConfigurationQuerySet(models.QuerySet):

    def get_baseline_complete_date(self, user):
        baseline_complete_date = None
        fitbit_account_user = FitbitAccountUser.objects.filter(user=user).prefetch_related('account').first()
        if fitbit_account_user:
            days = FitbitDay.objects.filter(
                account = fitbit_account_user.account,
                wore_fitbit = True
            ).order_by('date')[:10]
            days = list(days)
            if len(days) > 8:
                day_completed = days[7]
                baseline_complete_date = day_completed.date
        return baseline_complete_date

    def get_firsts(self):
        users = [config.user for config in self.prefetch_related('user').all()]
        for user in users:
            first_decision_service_request = AntiSedentaryServiceRequest.objects.filter(
                user = user,
                url__contains = 'decision'
            ) \
            .order_by('request_time') \
            .first()
            first_decision = AntiSedentaryDecision.objects.filter(
                user = user,
            ).order_by('created').first()
            first_real_time_sedentary_treated_decision = AntiSedentaryDecision.objects.filter(
                user = user,
                imputed = False,
                treated = True,
                sedentary = True,
                available = True
            ) \
            .order_by('created') \
            .first()
            
            yield {
                'username': user.username,
                'date_joined': user.date_joined,
                'baseline_complete_date': self.get_baseline_complete_date(user),
                'first_decision': first_decision,
                'first_decision_service_request': first_decision_service_request,
                'first_real_time_sedentary_treated_decision': first_real_time_sedentary_treated_decision,
            }


class Configuration(models.Model):
    user = models.ForeignKey(User, related_name="anti_sedentary_configuration", on_delete = models.CASCADE)
    enabled = models.BooleanField(default=False)

    objects = ConfigurationQuerySet.as_manager()

    def __str__(self):
        if self.enabled:
            return self.user.username + ' (enabled)'
        else:
            return self.user.username + ' (disabled)'

class AntiSedentaryMessageTemplate(MessageTemplate):
    pass

class AntiSedentaryServiceRequest(ServiceRequest):
    pass

class AntiSedentaryDecision(Decision):
    MESSAGE_TEMPLATE_MODEL = AntiSedentaryMessageTemplate

    objects = DecisionContextQuerySet.as_manager()

    def get_treatment_probability(self):
        return 0.15
