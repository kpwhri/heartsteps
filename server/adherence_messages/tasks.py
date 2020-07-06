from celery import shared_task
from import_export import resources
from import_export.fields import Field

from anti_sedentary.models import AntiSedentaryDecision
from walking_suggestions.models import WalkingSuggestionDecision
from fitbit_activities.models import FitbitDay
from fitbit_api.services import FitbitService
from push_messages.models import Message
from page_views.models import PageView
from watch_app.services import StepCountService as WatchAppStepCountService

from .models import AdherenceMetric
from .services import AdherenceService

@shared_task
def initialize_adherence(username):
    service = AdherenceService(username=username)
    service.initialize()

@shared_task
def send_adherence_message(username):
    service = AdherenceService(username=username)
    service.send_adherence_message()

@shared_task
def update_adherence(username):
    service = AdherenceService(username=username)
    service.update_adherence()


class DailyAdherenceResource(resources.Resource):
    date = Field()

    app_installed = Field()
    app_page_views = Field()
    app_used = Field()

    fitbit_worn = Field()
    fitbit_updated = Field()
    
    minutes_worn = Field()
    fitbit_step_count = Field()
    watch_app_step_count = Field()

    messages_sent = Field()
    messages_received = Field()
    messages_opened = Field()
    messages_engaged = Field()

    anti_sedentary_messages_sent = Field()
    anti_sedentary_messages_received = Field()
    anti_sedentary_messages_opened = Field()
    anti_sedentary_messages_engaged = Field()

    walking_suggestion_messages_sent = Field()
    walking_suggestion_messages_received = Field()
    walking_suggestion_messages_opened = Field()
    walking_suggestion_messages_engaged = Field()

    class Meta:
        export_order = [
            'date',
            'app_installed',
            'app_page_views',
            'app_used',
            'fitbit_updated',
            'minutes_worn',
            'fitbit_worn',
            'fitbit_step_count',
            'watch_app_step_count',
            'messages_sent',
            'messages_received',
            'messages_opened',
            'messages_engaged',
            'anti_sedentary_messages_sent',
            'anti_sedentary_messages_received',
            'anti_sedentary_messages_opened',
            'anti_sedentary_messages_engaged',
            'walking_suggestion_messages_sent',
            'walking_suggestion_messages_received',
            'walking_suggestion_messages_opened',
            'walking_suggestion_messages_engaged'
        ]
    
    def get_key(self, instance, key):
        if key in instance:
            return instance[key]
        else:
            return None

    def dehydrate_app_installed(self, instance):
        return self.get_key(instance, AdherenceMetric.APP_INSTALLED)

    def dehydrate_app_page_views(self, instance):
        return self.get_key(instance, 'app_page_views')

    def dehydrate_app_used(self, instance):
        return self.get_key(instance, AdherenceMetric.APP_USED)

    def dehydrate_fitbit_worn(self, instance):
        return self.get_key(instance, AdherenceMetric.FITBIT_WORN)

    def dehydrate_fitbit_updated(self, instance):
        return self.get_key(instance, AdherenceMetric.FITBIT_UPDATED)

    def dehydrate_date(self, instance):
        return instance['date'].strftime('%Y-%m-%d')

    def dehydrate_minutes_worn(self, instance):
        return self.get_key(instance, 'fitbit_minutes_worn')

    def dehydrate_fitbit_step_count(self, instance):
        return self.get_key(instance, 'fitbit_step_count')

    def dehydrate_watch_app_step_count(self, instance):
        return self.get_key(instance, 'watch_app_step_count')

    def dehydrate_messages_sent(self, instance):
        return self.get_key(instance, 'messages_sent')

    def dehydrate_messages_received(self, instance):
        return self.get_key(instance, 'messages_received')

    def dehydrate_messages_opened(self, instance):
        return self.get_key(instance, 'messages_opened')

    def dehydrate_messages_engaged(self, instance):
        return self.get_key(instance, 'messages_engaged')

    def dehydrate_anti_sedentary_messages_sent(self, instance):
        return self.get_key(instance, 'anti_sedentary_messages_sent')

    def dehydrate_anti_sedentary_messages_received(self, instance):
        return self.get_key(instance, 'anti_sedentary_messages_received')

    def dehydrate_anti_sedentary_messages_opened(self, instance):
        return self.get_key(instance, 'anti_sedentary_messages_opened')

    def dehydrate_anti_sedentary_messages_engaged(self, instance):
        return self.get_key(instance, 'anti_sedentary_messages_engaged')

    def dehydrate_walking_suggestion_messages_sent(self, instance):
        return self.get_key(instance, 'walking_suggestion_messages_sent')

    def dehydrate_walking_suggestion_messages_received(self, instance):
        return self.get_key(instance, 'walking_suggestion_messages_received')

    def dehydrate_walking_suggestion_messages_opened(self, instance):
        return self.get_key(instance, 'walking_suggestion_messages_opened')

    def dehydrate_walking_suggestion_messages_engaged(self, instance):
        return self.get_key(instance, 'walking_suggestion_messages_engaged')

def export_adherence_metrics(username, directory):
    try:
        adherence_service = AdherenceService(username = username)
    except AdherenceService.NoConfiguration:
        return False
    adherence_days = {}
    for metric in AdherenceMetric.objects.order_by('date').filter(user__username=username).all():
        date_string = metric.date.strftime('%Y-%m-%d')
        if date_string not in adherence_days:
            adherence_days[date_string] = {
                'date': metric.date
            }
        adherence_days[date_string][metric.category] = metric.value

    days = []
    for value in adherence_days.values():
        days.append(value)
    days.sort(key=lambda day: day['date'])

    try:
        fitbit_service = FitbitService(username=username)
        account = fitbit_service.account
        for day in days:
            try:
                fitbit_day = FitbitDay.objects.get(
                    account = account,
                    date = day['date']
                )
                day['fitbit_step_count'] = fitbit_day.step_count
                day['fitbit_minutes_worn'] = fitbit_day.get_minutes_worn()
            except FitbitDay.DoesNotExist:
                pass
    except FitbitService.NoAccount:
        account = None

    for day in days:

        day_service = DayService(username = username)
        day_start = day_service.get_start_of_day(day['date'])
        day_end = day_service.get_end_of_day(day['date'])

        day['app_page_views'] = PageView.objects.filter(
            user__username = username,
            time__range = [day_start, day_end]
        ).count()

        try:
            watch_app_step_count_service = WatchAppStepCountService(username=username)
            day['watch_app_step_count'] = watch_app_step_count_service.get_step_count_between(
                start = day_start,
                end = day_end
            )
        except WatchAppStepCountService.NoStepCountRecorded:
            day['watch_app_step_count'] = None

        def tally_messages(messages, prefix='messages'):
            messages_sent = 0
            messages_received = 0
            messages_opened = 0
            messages_engaged = 0

            for message in messages:
                if message.sent:
                    messages_sent += 1
                if message.received:
                    messages_received += 1
                if message.opened:
                    messages_opened += 1
                if message.engaged:
                    messages_engaged += 1

            day[prefix + '_sent'] = messages_sent
            day[prefix + '_received'] = messages_received
            day[prefix + '_opened'] = messages_opened
            day[prefix + '_engaged'] = messages_engaged

        messages = Message.objects.filter(
            recipient__username=username,
            created__range=[day_start, day_end]
        ).all()
        tally_messages(messages)

        anti_sedentary_messages = []
        anti_sedentary_decisions = AntiSedentaryDecision.objects.filter(
            user__username = username,
            time__range = [day_start, day_end]
        ).all()
        for decision in anti_sedentary_decisions:
            if decision.notification:
                anti_sedentary_messages.append(decision.notification)
        tally_messages(anti_sedentary_messages, prefix='anti_sedentary_messages')
        
        walking_suggestion_messages = []
        walking_suggestion_decisions = WalkingSuggestionDecision.objects.filter(
            user__username = username,
            time__range = [day_start, day_end]
        ).all()
        for decision in walking_suggestion_decisions:
            if decision.notification:
                walking_suggestion_messages.append(decision.notification)
        tally_messages(walking_suggestion_messages, prefix='walking_suggestion_messages')

    
    dataset = DailyAdherenceResource().export(queryset=days)
    write_csv_file(
        directory = directory,
        filename = '%s.adherence_metrics.csv' % (username),
        content = dataset.csv
    )
