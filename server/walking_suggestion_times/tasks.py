from walking_suggestion_times.models import SuggestionTime
from user_event_logs.models import EventLog

def create_default_suggestion_times(participant):
    EventLog.debug(participant.user)
    existing_suggestion_times = SuggestionTime.objects.filter(
        user=participant.user
    ).count()
    EventLog.debug(participant.user)
    if not existing_suggestion_times:
        EventLog.debug(participant.user)
        default_times = [
            (SuggestionTime.MORNING, 9, 0),
            (SuggestionTime.LUNCH, 12, 0),
            (SuggestionTime.MIDAFTERNOON, 14, 0),
            (SuggestionTime.EVENING, 17, 0),
            (SuggestionTime.POSTDINNER, 20, 0)
        ]
        EventLog.debug(participant.user)
        for category, hour, minute in default_times:
            EventLog.debug(participant.user)
            SuggestionTime.objects.create(
                user=participant.user,
                category=category,
                hour=hour,
                minute=minute
            )
