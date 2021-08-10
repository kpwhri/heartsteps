import participants
from participants.models import Participant
from django.dispatch import receiver
from django.db.models.signals import post_save
from feature_flags.models import FeatureFlags


@receiver(post_save, sender=Participant)
def create_feature_flags(sender, instance, created, **kwargs):
    if created and not FeatureFlags.exists(user=instance.user):
        FeatureFlags.create(
            user=instance.user, flags=instance.cohort.study.studywide_feature_flags)
