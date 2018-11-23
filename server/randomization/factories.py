from randomization.models import Decision

def make_decision_message(decision):
    if Message.objects.filter(id=decision.id).count() > 0:
        return False
    message = Message(
        decision = decision
    )
    message_template = message.get_message_template()
    if message_template:
        message.message_template = message_template
        message.save()
        return message
    else:
        return False
