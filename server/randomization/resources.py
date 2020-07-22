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
        'decision_time',
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
        # 'watch_step_count',
        # 'fitbit_step_count',
        # 'watch_step_count',
        # 'watch_step_count_previous_30_minutes',
        # 'watch_step_count_post_30_minutes',
        # 'fitbit_step_count',
        # 'fitbit_step_count_previous_30_minutes',
        # 'fitbit_step_count_post_30_minutes',
        # 'message',
        'sent_time',
        'received_time',
        'opened_time',
        'engaged_time',
        'location',
        # 'temperature',
        # 'precipitation_type',
        # 'precipitation_probability',
        'imputed',
        'created_time'
    ]

    decision_time = Field(column_name='Decision Time')
    # all_tags = Field(column_name='tags')
    sent_time = Field(column_name='Sent Time')
    received_time = Field(column_name='Received Time')
    opened_time = Field(column_name='Opened Time')
    engaged_time = Field(column_name='Engaged Time')
    # message = Field()

    # watch_step_count = Field()
    # watch_step_count_previous_30_minutes = Field()
    # watch_step_count_post_30_minutes = Field()
    # fitbit_step_count = Field()
    # fitbit_step_count_previous_30_minutes = Field()
    # fitbit_step_count_post_30_minutes = Field()

    unavailable_no_step_count_data = Field(column_name='Unavailable No Step Count Data')
    unavailable_not_sedentary = Field(column_name='Unavailable Not Sedentary')
    unavailable_notification_recently_sent = Field(column_name='Unavailabe Notification Recently Sent')
    unavailable_recently_active = Field(column_name='Unavailable Recently Active')
    unavailable_unreachable = Field(column_name='Unavailable Unreachable')
    unavailable_disabled = Field(column_name='Unavailable Disabled')
    unavailable_service_error = Field(column_name='Unavaiable Server Error')

    location = Field(column_name='Location')

    # temperature = Field()
    # precipitation_type = Field()
    # precipitation_probability = Field()

    created_time = Field(column_name='Created time')

    def format_datetime(self, dt):
        if dt:
            return dt.strftime('%Y-%m-%d %H:%M %z')
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

    def dehydrate_timezone(self, decision):
        return decision.timezone.zone

    def dehydrate_decision_time(self, decision):
        time = decision.time.astimezone(decision.timezone)
        return self.format_datetime(time)

    def dehydrate_created_time(self, decision):
        time = decision.created.astimezone(decision.timezone)
        return self.format_datetime(time)
    
    def dehydrate_all_tags(self, decision):
        return ', '.join(decision.get_context())

    def dehydrate_sent_time(self, decision):
        if decision.notification and decision.notification.sent:
            sent_time = decision.notification.sent.astimezone(decision.timezone)
            return self.format_datetime(sent_time)
        else:
            return None

    def dehydrate_received_time(self, decision):
        if decision.notification and decision.notification.received:
            received_time = decision.notification.received.astimezone(decision.timezone)
            return self.format_datetime(received_time)
        else:
            return None

    def dehydrate_opened_time(self, decision):
        if decision.notification and decision.notification.opened:
            opened_time = decision.notification.opened.astimezone(decision.timezone)
            return self.format_datetime(opened_time)
        else:
            return None

    def dehydrate_engaged_time(self, decision):
        if decision.notification and decision.notification.engaged:
            engaged_time = decision.notification.engaged.astimezone(decision.timezone)
            return self.format_datetime(engaged_time)
        else:
            return None

    def dehydrate_message(self, decision):
        if decision.message_template:
            return decision.message_template.body
        else:
            return None

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

    def dehydrate_location(self, decision):
        return decision.get_location_type()

    def dehydrate_temperature(self, decision):
        return decision.temperature

    def dehydrate_precipitation_type(self, decision):
        return decision.precipitation_type

    def dehydrate_precipitation_probability(self, decision):
        return decision.precipitation_probability

