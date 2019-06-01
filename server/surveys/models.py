import uuid
import random

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
        return list(self.answer_set.order_by('order', 'created').all())

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
    
    class OptionDoesNotExist(RuntimeError):
        pass

    class AnswerDoesNotExist(RuntimeError):
        pass
    
    QUESTION_MODEL = Question

    @property
    def id(self):
        return str(self.uuid)

    @property
    def questions(self):
        questions = self.surveyquestion_set.order_by('order').all()
        return list(questions)
    
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
            question = self.QUESTION_MODEL.objects.get(name=name)
        except self.QUESTION_MODEL.DoesNotExist:
            raise self.QuestionDoesNotExist('No question with name ' + name)
        survey_question = SurveyQuestion.objects.create(
            survey = self,
            question = question,
            name = question.name,
            label = question.label,
            description = question.description,
            order = SurveyQuestion.objects.filter(survey=self).count() + 1
        )
        for answer in question.answers:
            survey_question.add_option(answer)

    def randomize_questions(self):
        SurveyQuestion.objects.filter(survey=self).delete()

        questions = list(self.QUESTION_MODEL.objects.all())
        random.shuffle(questions)
        for question in questions:
            self.add_question(question.name)
    
    def save_response(self, question_name, response = None):
        question = self.get_question(question_name)
        if response is None:
            self.create_response(question)
        else:
            try:
                answer = question.get_option(response)
                self.create_response(question, answer)
            except SurveyQuestion.OptionDoesNotExist:
                raise self.OptionDoesNotExist(response + ' is not a valid option')

    def create_response(self, question, answer=None):
        SurveyResponse.objects.create(
            survey = self,
            question = question,
            answer = answer
        )
        self.updated = timezone.now()
        self.save()

    def get_answer(self, question=None, question_name=None):
        if question_name:
            question = self.get_question
        try:
            response = SurveyResponse.objects.get(
                survey = self,
                question = question
            )
            return response.answer.value
        except SurveyResponse.DoesNotExist:
            raise self.AnswerDoesNotExist('No answer for question')

    def get_answers(self):
        answers = {}
        for question in self.questions:
            answers[question.name] = None
        for survey_response in SurveyResponse.objects.filter(survey=self).all():
            answers[survey_response.question.name] = survey_response.answer.value
        return answers

    def get_questions(self):
        return [question.name for question in self.questions]

    def get_question_label(self, question_name):
        for question in self.questions:
            if question.name == question_name:
                return question.label
        return question_name

    def get_answer_label(self, question_name, answer_value):
        for question in self.questions:
            if question.name == question_name:
                for option in question.options:
                    if option.value == answer_value:
                        return option.label
        return answer_value


    @property
    def answered(self):
        response_count = SurveyResponse.objects.filter(
            survey = self
        ).count()
        if response_count > 0:
            return True
        else:
            return False
    

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

    class OptionDoesNotExist(RuntimeError):
        pass

    @property
    def options(self):
        options = self.answers.order_by('order').all()
        return list(options)

    def add_option(self, answer):
        SurveyAnswer.objects.create(
            question = self,
            answer = answer,
            label = answer.label,
            value = answer.value,
            order = SurveyAnswer.objects.filter(question=self).count() + 1
        )

    def add_new_options(self, label, value):
        SurveyAnswer.objects.create(
            question = self,
            label = label,
            value = value,
            order = SurveyAnswer.objects.filter(question=self).count()+1
        )

    def get_option(self, value):
        try:
            return self.answers.get(value=value)
        except SurveyAnswer.DoesNotExist:
            raise self.OptionDoesNotExist('Option does not exist')

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
