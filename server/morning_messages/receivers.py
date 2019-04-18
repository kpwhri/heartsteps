from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver

from morning_messages.models import Configuration, MorningMessage, MorningMessageDecision, MorningMessageSurvey
from morning_messages.services import MorningMessageDecisionService

@receiver(pre_save, sender=Configuration)
def manage_daily_task(sender, instance, **kwargs):
    if not instance.daily_task:
        instance.create_daily_task()
    if instance.enabled:
        instance.daily_task.enable()
    if not instance.enabled:
        instance.daily_task.disable()

@receiver(pre_delete, sender=Configuration)
def delete_daily_task(sender, instance, **kwargs):
    if instance.daily_task:
        instance.destroy_daily_task()


@receiver(pre_save, sender=MorningMessage)
def morning_message_generate_decision(sender, instance, **kwargs):
    morning_message = instance

    if morning_message.message_decision:
        decision_service = MorningMessageDecisionService(morning_message.message_decision)
        message_template = decision_service.get_message_template()

        morning_message.notification = message_template.body
        if hasattr(message_template, 'anchor_message'):
            morning_message.text = message_template.body
            morning_message.anchor = message_template.anchor_message
        else:
            morning_message.text = None
            morning_message.anchor = None

@receiver(pre_save, sender=MorningMessage)
def morning_message_create_survey(sender, instance, **kwargs):
    morning_message = instance
    
    if not morning_message.survey:
        survey = MorningMessageSurvey.objects.create(
            user = morning_message.user
        )
        survey.randomize_questions()

        morning_message.survey = survey
