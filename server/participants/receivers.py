import participants
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from feature_flags.models import FeatureFlags
from participants.models import Study, Cohort, Participant

# Commented by Junghwan: We don't need to do this. During user initialization (i.e., the first log in), 
#   new user is created. Then, as a part of initialization steps, FeatureFlags is created.

# @receiver(post_save, sender=Participant)
# def create_feature_flags(sender, instance, created, **kwargs):
#     if created and instance.cohort and instance.user and not FeatureFlags.exists(user=instance.user):
#         FeatureFlags.create(
#             user=instance.user, flags=instance.cohort.study.studywide_feature_flags)


@receiver(pre_save, sender=Study)
def update_feature_flags(sender, instance, **kwargs):
    # get cohorts inside this study
    cohorts = Cohort.objects.filter(study=instance)
    for cohort in cohorts:
        # get participants in this cohort
        participants = Participant.objects.filter(cohort=cohort)
        for participant in participants:
            if FeatureFlags.exists(user=participant.user):
                new_studywide_feature_flags_list = instance.studywide_feature_flags.split(
                    ", ")
                current_feature_flag_list = FeatureFlags.get(
                    user=participant.user).flags.split(", ")
                # will always return a unique Study object because name attribute is unique for each study
                old_studywide_feature_flags_list = Study.objects.get(
                    name=instance.name).studywide_feature_flags.split(", ")
                # print("FF: new_studywide_feature_flags_list - ",
                #       new_studywide_feature_flags_list)
                # print("FF: old_studywide_feature_flags_list - ",
                #       old_studywide_feature_flags_list)
                # print("FF: current_feature_flag_list - ",
                #       current_feature_flag_list)
                # performs union operator on both feature flag lists without repetition

                # i.e. old studywide list = ['hi', 'hello', 'wow']
                # new studywide list = ['hi', 'wow', 'yikes']
                # current stored feature flags list for user = ['hi', 'hello', 'wow', 'a_unique_flag']
                # final flag to be used in update = ['hi', 'wow', 'yikes', 'a_unique_flag']
                union_flags = list(
                    set(new_studywide_feature_flags_list)
                    | set(current_feature_flag_list))

                # TODO: test more and make more efficient
                outdated_flags = ['']
                for old_flag in old_studywide_feature_flags_list:
                    if old_flag not in new_studywide_feature_flags_list:
                        outdated_flags.append(old_flag)

                for old_flag in outdated_flags:
                    if old_flag in union_flags:
                        # print("FF: union removed - ", old_flag)
                        union_flags.remove(old_flag)

                final_flags = ", ".join(union_flags)
                # print("FF: final flags list - ", union_flags)
                # print("FF: final flags string - ", final_flags)

                FeatureFlags.update(user=participant.user, flags=final_flags)
