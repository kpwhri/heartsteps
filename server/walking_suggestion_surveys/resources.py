from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget

from .models import Decision

class WalkingSuggestionSurveyDecisionResource(resources.ModelResource):

    decision_id = Field(
        attribute = 'id',
        column_name = 'Decision ID'
    )
    heartsteps_id = Field(
        column_name = 'HeartSteps ID'
    )
    decision_date = Field(
        column_name = 'Decision Date'
    )
    decision_time = Field(
        column_name = 'Decision Time'
    )
    decision_timezone = Field(
        column_name = 'Timezone'
    )

    treated = Field(
        attribute = 'treated',
        column_name = 'Treated'
    )
    treatment_probability = Field(
        attribute = 'treatment_probability',
        column_name = 'Treatment Probability'
    )

    notification_id = Field(
        attribute = 'notification__id',
        column_name = 'Notification ID'
    )
    notification_sent = Field(
        attribute = 'notification__sent',
        column_name = 'Notification Sent',
        widget = DateTimeWidget(format = '%Y-%m-%d %H:%M:%S')
    )
    notification_received = Field(
        attribute = 'notification__received',
        column_name = 'Notification Received',
        widget = DateTimeWidget(format = '%Y-%m-%d %H:%M:%S')
    )
    notification_opened = Field(
        attribute = 'notification__opened',
        column_name = 'Notification Opened',
        widget = DateTimeWidget(format = '%Y-%m-%d %H:%M:%S')
    )

    class Meta:
        model = Decision
        fields = []

    def format_date(self, _datetime):
        return _datetime.strftime('%Y-%m-%d')
    
    def format_time(self, _datetime):
        return _datetime.strftime('%H:%M:%S')

    def dehydrate_heartsteps_id(self, decision):
        return decision.user.username

    def dehydrate_decision_date(self, decision):
        return self.format_date(decision.randomized_at)
    
    def dehydrate_decision_time(self, decision):
        return self.format_time(decision.randomized_at)

    def dehydrate_decision_timezone(self, decision):
        return decision.randomized_at.tzname()

    def after_export(self, queryset, data, *args, **kwargs):
        questions = {}
        for decision in queryset:
            if decision.survey and hasattr(decision.survey, '_questions'):
                for question in decision.survey._questions:
                    if question.id not in questions.keys():
                        questions[question.name] = {
                            'name': question.name,
                            'answers': []
                        }
        for decision in queryset:
            if decision.survey and hasattr(decision.survey, '_answers'):
                for question_name, answer in decision.survey._answers.items():
                    questions[question_name]['answers'].append(answer.value)
            else:
                for question in questions.values():
                    question['answers'].append(None)
        
        for question_key in sorted(questions.keys()):
            question = questions[question_key]
            data.append_col(question['answers'], header=question['name'])
