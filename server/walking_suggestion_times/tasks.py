from walking_suggestion_times.models import SuggestionTime
from user_event_logs.models import EventLog

def create_default_suggestion_times(participant):
    existing_suggestion_times = SuggestionTime.objects.filter(
        user=participant.user
    ).count()
    if not existing_suggestion_times:
        default_times = [
            (SuggestionTime.MORNING, 9, 0),
            (SuggestionTime.LUNCH, 12, 0),
            (SuggestionTime.MIDAFTERNOON, 14, 0),
            (SuggestionTime.EVENING, 17, 0),
            (SuggestionTime.POSTDINNER, 20, 0)
        ]
        for category, hour, minute in default_times:
            SuggestionTime.objects.create(
                user=participant.user,
                category=category,
                hour=hour,
                minute=minute
            )
