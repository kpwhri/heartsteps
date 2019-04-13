import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Question(models.Model):
    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=250)
    description = models.CharField(max_length=250, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def answers(self):
        return list(self.answer_set.all())

    def __str__(self):
        return self.name

class Answer(models.Model):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    question = models.ForeignKey(Question)
    order = models.IntegerField(null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Survey(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(User)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class QuestionDoesNotExist(RuntimeError):
        pass

    @property
    def id(self):
        return str(self.uuid)

    @property
    def questions(self):
        return list(self.surveyquestion_set.all())
    
    def get_question(self, name):
        try:
            return SurveyQuestion.objects.get(
                survey = self,
                name = name
            )
        except SurveyQuestion.DoesNotExist:
            raise self.QuestionDoesNotExist('Question not part of survey')

    def add_question(self, name):
        try:
            question = Question.objects.get(name=name)
        except Question.DoesNotExist:
            raise self.QuestionDoesNotExist('No question with name ' + name)
        survey_question = SurveyQuestion.objects.create(
            survey = self,
            question = question,
            name = question.name,
            label = question.label,
            description = question.description
        )
        for answer in question.answers:
            SurveyAnswer.objects.create(
                question = survey_question,
                answer = answer,
                label = answer.label,
                value = answer.value,
                order = answer.order
            )
    
    def save_response(self, question_name, response = None):
        question = self.get_question(question_name)
        if response is None:
            self.create_response(question)
        else:
            answer = question.get_answer(response)
            self.create_response(question, answer)

    def create_response(self, question, answer=None):
        SurveyResponse.objects.create(
            survey = self,
            question = question,
            answer = answer
        )
        self.updated = timezone.now()
        self.save()
    

class SurveyQuestion(models.Model):
    question = models.ForeignKey(
        Question,
        related_name="+",
        on_delete=models.SET_NULL,
        null=True
    )

    survey = models.ForeignKey(Survey)
    order = models.IntegerField(null=True)

    name = models.CharField(max_length=100)
    label = models.CharField(max_length=250)
    description = models.CharField(max_length=250, null=True, blank=True)

    def get_answer(self, value):
        try:
            return self.answers.get(value=value)
        except SurveyAnswer.DoesNotExist:
            raise RuntimeError('Answer does not exist')

class SurveyAnswer(models.Model):
    answer = models.ForeignKey(
        Answer,
        related_name = "+",
        on_delete = models.SET_NULL,
        null = True
    )

    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    
    question = models.ForeignKey(SurveyQuestion, related_name="answers")
    order = models.IntegerField(null=True)

class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey)
    question = models.ForeignKey(SurveyQuestion)
    answer = models.ForeignKey(SurveyAnswer, null=True)
