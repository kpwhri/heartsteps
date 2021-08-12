from django.contrib import admin
from django.contrib import messages

from behavioral_messages.admin import MessageTemplateAdmin
from surveys.admin import QuestionAdmin

from .models import Configuration
from .models import MorningMessage
from .models import MorningMessageTemplate
from .models import MorningMessageQuestion
from .services import MorningMessageService

def send_morning_message(modeladmin, request, queryset):
    for configuration in queryset.all():
        service = MorningMessageService(configuration = configuration)
        service.send_notification(test=True)
        messages.add_message(
            request,
            messages.SUCCESS, 
            'Sent morning message to %s' % (configuration.user.username)
            )

class MorningMessageConfigurationAdmin(admin.ModelAdmin):
    list_display = ['username', 'enabled']
    fields = ['user', 'enabled', 'next_morning_message']
    # readonly_fields = ['user', 'next_morning_message']
    readonly_fields = ['next_morning_message']
    actions = [send_morning_message]

    def username(self, instance):
        return instance.user.username

    def next_morning_message(self, instance):
        if instance.enabled:
            return instance.daily_task.get_next_run_time().strftime('%Y-%m-%d %H:%M')
        else:
            return 'Morning message not enabled'

admin.site.register(Configuration, MorningMessageConfigurationAdmin)

class MorningMessageAdmin(admin.ModelAdmin):
    list_display = ['username', 'date', 'was_sent', 'was_received', 'completed_survey']
    date_hierarchy = 'date'
    exclude = ['randomized']
    readonly_fields = [
        'user',
        'date',
        'timezone',
        'message_frame',
        'anchor_message',
        'survey_results',
        'notification_sent',
        'notification_received',
        'notification_opened',
        'notification_engaged'
        ]

    def anchor_message(self, morning_message):
        return morning_message.anchor

    def message_frame(self, morning_message):
        return morning_message.message_decision.framing

    def completed_survey(self, morning_message):
        return morning_message.survey.answered
    completed_survey.boolean = True

    def notification_sent(self, morning_message):
        tz = morning_message.get_timezone()
        notification = morning_message.get_notification()
        if notification and notification.sent:
            return notification.sent.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
        return None

    def notification_received(self, morning_message):
        tz = morning_message.get_timezone()
        notification = morning_message.get_notification()
        if notification and notification.received:
            return notification.received.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
        return None

    def notification_opened(self, morning_message):
        tz = morning_message.get_timezone()
        notification = morning_message.get_notification()
        if notification and notification.opened:
            return notification.opened.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
        return None

    def notification_engaged(self, morning_message):
        tz = morning_message.get_timezone()
        notification = morning_message.get_notification()
        if notification and notification.engaged:
            return notification.engaged.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
        return None

    def timezone(self, morning_message):
        return morning_message.get_timezone().zone

    def was_sent(self, morning_message):
        notification = morning_message.get_notification()
        if notification and notification.sent:
            return True
        return False
    was_sent.boolean = True

    def was_received(self, morning_message):
        notification = morning_message.get_notification()
        if notification and notification.received:
            return True
        else:
            return False
    was_received.boolean = True

    def username(self, morning_message):
        return morning_message.user.username

    def survey_results(self, morning_message):
        results_list = []
        answers = morning_message.survey.get_answers()
        for question in morning_message.survey.get_questions():
            question_label = morning_message.survey.get_question_label(question)
            answer_label = morning_message.survey.get_answer_label(question, answers[question])
            results_list.append({
                'question': question_label,
                'answer': answer_label
            })
        results = '<dl>%s</dl>' % (
            ''.join(['<dt>%(question)s</dt><dd>%(answer)s</dd>' % result for result in results_list])
        )
        answered_text = 'Was not answered'
        if morning_message.survey.answered:
            answered_text = 'Answered'
        return '<p>%s</p>%s' % (answered_text,results)
    survey_results.allow_tags = True

admin.site.register(MorningMessage, MorningMessageAdmin)

class MorningMessageTemplateAdmin(MessageTemplateAdmin):
    pass
admin.site.register(MorningMessageTemplate, MorningMessageTemplateAdmin)

class MorningMessageQuestionAdmin(QuestionAdmin):
    pass

admin.site.register(MorningMessageQuestion, MorningMessageQuestionAdmin)

