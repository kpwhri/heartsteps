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
                'kind': question.kind,
                'description': question.description,
                'options': [{'label': option.label, 'value': option.value } for option in question.options]
            })
        
        representation['id'] = str(instance.uuid)
        representation['completed'] = instance.answered
        representation['questions'] = questions
        
        # might need to download responses here.

        return representation

class SurveyShirinker:
    def __init__(self, survey_obj):
        self.representation = {}
        
        self.representation['id'] = str(survey_obj.uuid)
    
    def to_json(self):
        import json
        
        return json.dumps(self.representation)
    
class SurveyExpander:
    def __init__(self, survey_uuid):
        self.instance = Survey.objects.get(uuid=survey_uuid)
        
        self.representation = {}
        
        questions = []
        for question in self.instance.questions:
            questions.append({
                'name': question.name,
                'label': question.label,
                'kind': question.kind,
                'description': question.description,
                'options': [{'label': option.label, 'value': option.value } for option in question.options]
            })
        
        self.representation['id'] = str(self.instance.uuid)
        self.representation['completed'] = self.instance.answered
        self.representation['questions'] = questions
        
        # might need to download responses here.
    
    def to_json(self):
        import json
        
        return json.dumps(self.representation)