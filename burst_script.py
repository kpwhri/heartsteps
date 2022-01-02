from participants.models import Participant
from burst_periods.models import Configuration as BurstPeriodConfiguration
from activity_surveys.models import Configuration as ActivitySurveyConfiguration
from walking_suggestion_surveys.models import Configuration as WalkingSuggestionSurveyConfiguration

# NOTE: using Participant instead of DashboardParticipant in live code
current_heartsteps_id = 'test-patrick'
participant = Participant.objects.get(heartsteps_id=current_heartsteps_id)
burst_period_config_obj = BurstPeriodConfiguration.objects.get(user=participant.user)


def get_burst_configuration():
    try:
        return BurstPeriodConfiguration.objects \
            .prefetch_burst_periods() \
            .get(
                user=participant.user
            )
    except BurstPeriodConfiguration.DoesNotExist:
        return None



def setup_burst(participant, request_type):
    config = get_burst_configuration()
    if request_type == "enable":
        config.enabled = True
        config.save()
    elif request_type == "disable":
        config.enabled = False
        config.save()
    if request_type == "create":
        if config:
            config.delete()
        BurstPeriodConfiguration.objects.create(user=participant.user)
    if request_type == "create-daily-task":
        if config.daily_task:
            config.daily_task.delete()
        config.daily_task = config.create_daily_task()
        config.save()


setup_burst(participant, "enable")

def burst_activity_surveys():
    update_activity_survey_probability(1)


def burst_walking_suggestion_surveys():
    update_walking_suggestion_survey_treatment_probability(1)


# NOTE: we use user in live code, not participant.user
# print functions added to help debug
def update_activity_survey_probability(treatment_probability):
    try:
        configuration = ActivitySurveyConfiguration.objects.get(
            user = participant.user
        )
        configuration.treatment_probability = treatment_probability
        print("activity service treatment_probability: ", treatment_probability)
        configuration.save()
    except ActivitySurveyConfiguration.DoesNotExist:
        print("EXCEPTION: ActivitySurveyConfiguration.DoesNotExist")
        pass


# NOTE: we use user in live code, not participant.user
# print functions added to help debug
def update_walking_suggestion_survey_treatment_probability(treatment_probability):
    try:
        configuration = WalkingSuggestionSurveyConfiguration.objects.get(
            user = participant.user
        )
        configuration.treatment_probability = treatment_probability
        print("walking suggestion treatment_probability: ", treatment_probability)
        configuration.save()
    except WalkingSuggestionSurveyConfiguration.DoesNotExist:
        print("EXCEPTION: WalkingSuggestionSurveyConfiguration.DoesNotExist")
        pass


def normalize_activity_surveys():
    update_activity_survey_probability(0.2)


def normalize_walking_suggestion_surveys():
    update_walking_suggestion_survey_treatment_probability(0)


def burst_intervention_configurations():
    burst_activity_surveys()
    burst_walking_suggestion_surveys()


def normalize_intervention_configurations():
    normalize_activity_surveys()
    normalize_walking_suggestion_surveys()

# NOTE: the actual changing of interventions is done in config.save()
# we are emulating the changes using copies of the functions defined above
# we must re-run config.save() to reflect changes in dashboard
# emulation helps understand where faulty logic might be at play
# the actual config.save() function is below
def setup_burst_advanced(participant, request_type):
    config = get_burst_configuration()
    if request_type == "enable":
        config.enabled = True
        if config.enabled:
            burst_intervention_configurations()
        else:
            normalize_intervention_configurations()
        config.save()
    elif request_type == "disable":
        config.enabled = False
        if config.enabled:
            burst_intervention_configurations()
        else:
            normalize_intervention_configurations()
        config.save()
    if request_type == "create":
        if config:
            config.delete()
        BurstPeriodConfiguration.objects.create(user=participant.user)
    if request_type == "create-daily-task":
        if config.daily_task:
            config.daily_task.delete()
        config.daily_task = config.create_daily_task()
        if config.enabled:
            burst_intervention_configurations()
        else:
            normalize_intervention_configurations()
        config.save()


# FOR REFERENCE: the actual config.save() function 

# def save(self, *args, **kwargs):
#     super().save(*args, **kwargs)
#     if self.enabled:
#         self.burst_intervention_configurations()
#     else:
#         self.normalize_intervention_configurations()


