from randomization.models import Message, Decision

def make_decision_message(decision):
    if Message.objects.filter(id=decision.id).count() > 0:
        return False
    message = Message(
        decision = decision
    )
    if message.get_message_template():
        message.save()
        return message
    else:
        return False
