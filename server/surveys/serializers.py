from rest_framework import serializers

from .models import Survey, SurveyQuestion, SurveyAnswer

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = []
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        questions = []
        for question in instance.questions:
            questions.append({
                'name': question.name,
                'label': question.label,
                'description': question.description,
                'options': [{'label': option.label, 'value': option.value } for option in question.options]
            })
        representation['questions'] = questions

        representation['completed'] = instance.answered

        return representation

