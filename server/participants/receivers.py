import participants
from django.dispatch import receiver
from django.db.models.signals import post_save
from feature_flags.models import FeatureFlags
from participants.models import Study, Cohort, Participant


@receiver(post_save, sender=Participant)
def create_feature_flags(sender, instance, created, **kwargs):
    if created and instance.cohort and instance.user and not FeatureFlags.exists(user=instance.user):
        FeatureFlags.create(
            user=instance.user, flags=instance.cohort.study.studywide_feature_flags)


@receiver(post_save, sender=Study)
def update_feature_flags(sender, instance, created, **kwargs):
    if not created:
        # get cohorts inside this study
        cohorts = Cohort.objects.filter(study=instance)
        for cohort in cohorts:
            # get participants in this cohort
            participants = Participant.objects.filter(cohort=cohort)
            for participant in participants:
                if FeatureFlags.exists(user=participant.user):
                    FeatureFlags.update(
                        user=participant.user, flags=participant.cohort.study.studywide_feature_flags)
