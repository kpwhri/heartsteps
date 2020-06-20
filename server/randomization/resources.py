from datetime import timedelta

from fitbit_activities.services import FitbitStepCountService
from watch_app.services import StepCountService as WatchAppStepCountService

from import_export import resources
from import_export.fields import Field
from import_export.admin import ExportMixin

class DecisionResource(resources.ModelResource):

    FIELDS = [
        'id',
        'user__username',
        'test',
        'imputed',
        'local_time',
        'sedentary',
        'available',
        'unavailable_no_step_count_data',
        'unavailable_not_sedentary',
        'unavailable_recently_active',
        'unavailable_notification_recently_sent',
        'unavailable_unreachable',
        'unavailable_disabled',
        'unavailable_service_error',
        'treated',
        'treatment_probability',
        'watch_step_count',
        'fitbit_step_count',
        'watch_step_count',
        'watch_step_count_previous_30_minutes',
        'watch_step_count_post_30_minutes',
        'fitbit_step_count',
        'fitbit_step_count_previous_30_minutes',
        'fitbit_step_count_post_30_minutes',
        'message',
        'sent_time',
        'received_time',
        'opened_time',
        'engaged_time',
        'location_tag',
        'location_imputed',
        'temperature',
        'precipitation_type',
        'precipitation_probability'
    ]

    local_time = Field(column_name='time')
    all_tags = Field(column_name='tags')
    sent_time = Field()
    received_time = Field()
    opened_time = Field()
    engaged_time = Field()
    message = Field()

    watch_step_count = Field()
    watch_step_count_previous_30_minutes = Field()
    watch_step_count_post_30_minutes = Field()
    fitbit_step_count = Field()
    fitbit_step_count_previous_30_minutes = Field()
    fitbit_step_count_post_30_minutes = Field()

    unavailable_no_step_count_data = Field()
    unavailable_not_sedentary = Field()
    unavailable_notification_recently_sent = Field()
    unavailable_recently_active = Field()
    unavailable_unreachable = Field()
    unavailable_disabled = Field()
    unavailable_service_error = Field()

    location_tag = Field()
    location_imputed = Field()

    temperature = Field()
    precipitation_type = Field()
    precipitation_probability = Field()

    def format_datetime(self, time):
        if time:
            return time.strftime('%Y-%m-%d %H:%M %z')
        else:
            return ''

    def get_fitbit_step_count(self, user, start, end):
        service = FitbitStepCountService(user = user)
        return service.get_step_count_between(
            start = start,
            end = end
        )

    def get_watch_app_step_count(self, user, start, end):
        service = WatchAppStepCountService(user = user)
        try:
            return service.get_step_count_between(
                start = start,
                end = end
            )
        except WatchAppStepCountService.NoStepCountRecorded:
            return None

    def dehydrate_local_time(self, decision):
        time = decision.get_local_datetime()
        return self.format_datetime(time)
    
    def dehydrate_all_tags(self, decision):
        return ', '.join(decision.get_context())

    def dehydrate_sent_time(self, decision):
        if decision.notification:
            return self.format_datetime(decision.notification.sent)
        else:
            return ''

    def dehydrate_received_time(self, decision):
        if decision.notification:
            return self.format_datetime(decision.notification.received)
        else:
            return ''

    def dehydrate_opened_time(self, decision):
        if decision.notification:
            return self.format_datetime(decision.notification.opened)
        else:
            return ''

    def dehydrate_engaged_time(self, decision):
        if decision.notification:
            return self.format_datetime(decision.notification.engaged)
        else:
            return ''

    def dehydrate_message(self, decision):
        if decision.message_template:
            return decision.message_template.body
        else:
            return ''

    def dehydrate_watch_step_count(self, decision):
        return self.get_watch_app_step_count(
            user = decision.user,
            start = decision.time - timedelta(minutes=40),
            end = decision.time
        )

    def dehydrate_watch_step_count_previous_30_minutes(self, decision):
        return self.get_watch_app_step_count(
            user = decision.user,
            start = decision.time - timedelta(minutes=30),
            end = decision.time
        )

    def dehydrate_watch_step_count_post_30_minutes(self, decision):
        return self.get_watch_app_step_count(
            user = decision.user,
            start = decision.time,
            end = decision.time + timedelta(minutes=30)
        )

    def dehydrate_fitbit_step_count(self, decision):
        return self.get_fitbit_step_count(
            user = decision.user,
            start = decision.time - timedelta(minutes=40),
            end = decision.time
        )

    def dehydrate_fitbit_step_count_previous_30_minutes(self, decision):
        return self.get_fitbit_step_count(
            user = decision.user,
            start = decision.time - timedelta(minutes=30),
            end = decision.time
        )

    def dehydrate_fitbit_step_count_post_30_minutes(self, decision):
        return self.get_fitbit_step_count(
            user = decision.user,
            start = decision.time,
            end = decision.time + timedelta(minutes=30)
        )

    def dehydrate_unavailable_no_step_count_data(self, decision):
        return decision.unavailable_no_step_count_data

    def dehydrate_unavailable_not_sedentary(self, decision):
        return decision.unavailable_not_sedentary

    def dehydrate_unavailable_recently_active(self, decision):
        return decision.unavailable_recently_active

    def dehydrate_unavailable_notification_recently_sent(self, decision):
        return decision.unavailable_notification_recently_sent

    def dehydrate_unavailable_unreachable(self, decision):
        return decision.unavailable_unreachable

    def dehydrate_unavailable_disabled(self, decision):
        return decision.unavailable_disabled

    def dehydrate_unavailable_service_error(self, decision):
        return decision.unavailable_service_error

    def dehydrate_location_tag(self, decision):
        return decision.get_location_type()

    def dehydrate_location_imputed(self, decision):
        if decision.get_location():
            return False
        else:
            return True

    def dehydrate_temperature(self, decision):
        print('dehydtrate temp', decision.temperature)
        return decision.temperature

    def dehydrate_precipitation_type(self, decision):
        return decision.precipitation_type

    def dehydrate_precipitation_probability(self, decision):
        return decision.precipitation_probability

