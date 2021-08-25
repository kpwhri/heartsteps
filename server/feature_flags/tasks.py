from os import name
from celery import shared_task
from participants.models import Cohort, Study, Participant
from feature_flags.models import FeatureFlags
from random import randint


class MultipleCohortException(Exception):
    # TODO: exception exists because name field is not unique=True, maybe refactor?
    pass


class StudyDoesNotExistException(Exception):
    pass


def apply_flags_to_participants(participants, flags: str, percentage: int) -> bool:
    """applies new flags across a percentage of these participants

        Args:
            participants (Participant): a list of Participant object instances
            flags (str): new feature flags

        Returns:
            success (bool): true if successfully completed, useful if run asynchronously using Celery
    """
    for participant in participants:
        # TODO: make sure rand will keep re-generating diff values each loop iteration
        rand = randint(1, 100)
        if rand <= percentage:
            apply_flags_to_participant(participant, flags)
    return True


def apply_flags_to_participant(participant: Participant, flags: str) -> bool:
    """applies new flags to this participant

        Args:
            participant (Participant): a Participant object instance
            flags (str): new feature flags

        Returns:
            success (bool): true if successfully completed, useful if run asynchronously using Celery
    """
    flags_list = flags.split(", ")
    ff, _ = FeatureFlags.create_or_get(user=participant.user)
    for flag in flags_list:
        FeatureFlags.add_flag(obj=ff, flag=flag)
    return True


def apply_flags_to_cohort(cohort: Cohort, flags: str, percentage: int) -> bool:
    """applies new flags across a percentage of these participants in this cohort

        Args:
            cohort (Cohort): a Cohort object instance
            flags (str): new feature flags
            percentage (int): optional, a number between [1,100], 
                              applies flags to only only that percentage of participants
                              if no value is provided, flags will be applied to 100% of target participants

        Returns:
            success (bool): true if successfully completed, useful if run asynchronously using Celery
    """
    participants = Participant.objects.filter(cohort=cohort)
    apply_flags_to_participants(participants, flags, percentage)
    return True


def apply_flags_to_study(study: Study, flags: str, percentage: int) -> bool:
    """applies new flags across a percentage of these participants in this study

        Args:
            study (Study): a Study object instance
            flags (str): new feature flags
            percentage (int): optional, a number between [1,100], 
                              applies flags to only only that percentage of participants
                              if no value is provided, flags will be applied to 100% of target participants

        Returns:
            success (bool): true if successfully completed, useful if run asynchronously using Celery
    """
    cohorts = Cohort.objects.filter(study=study)
    participants = []
    # participants = [Participant.objects.filter(cohort=cohort) for cohort in cohorts]
    for cohort in cohorts:
        participants.extend(Participant.objects.filter(cohort=cohort))
    apply_flags_to_participants(participants, flags, percentage)
    return True


@shared_task
def apply_flags(flags: str, study_name: str, cohort_name: str = None, percentage: int = 100) -> bool:
    """applies new flags across a percentage of all participants in a study or in a specific cohort

        Args:
            flags (str): new feature flags
            study_name (str): name of a study
            cohort_name (str): optional, including cohort_name only apply flags to that cohort
            percentage (int): optional, a number between [1,100], 
                              applies flags to only only that percentage of participants
                              if no value is provided, flags will be applied to 100% of target participants

        Raises:
            StudyDoesNotExistException: if the study does not exist
            MultipleCohortException: if the multiple cohorts with that cohort_name exist
            TypeError: if cohort_name is not a string
            ValueError: if percentage is not between [1,100] inclusive

        Returns:
            success (bool): true if successfully completed, useful if run asynchronously using Celery
    """
    study = Study.objects.get(name=study_name)
    if not study:
        raise StudyDoesNotExistException
    if not isinstance(cohort_name, str):
        raise TypeError("cohort name needs to be a string")
    if percentage > 100 or percentage < 1:
        raise ValueError("percentage should be between [1,100] inclusive")

    # apply to only cohort with cohort_name
    if cohort_name:
        cohort = Cohort.objects.filter(name=cohort_name)
        if len(cohort) > 1:
            raise MultipleCohortException
        apply_flags_to_cohort(cohort, flags, percentage)

    # apply to all cohorts in study
    else:
        apply_flags_to_study(study, flags, percentage)

    return True
