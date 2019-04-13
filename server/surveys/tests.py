from django.test import TestCase

from .models import Question, Answer, User, Survey, SurveyQuestion, SurveyAnswer, SurveyResponse

class SurveyModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

        first_question = Question.objects.create(
            name="first question",
            label="This is the first question"
        )
        Answer.objects.create(
            question = first_question,
            label = "First answer",
            value = "first"
        )
        Answer.objects.create(
            question = first_question,
            label = "Second answer",
            value = "second"
        )

        Question.objects.create(
            name="second question",
            label="This is the second question"
        )

    def testCreateSurvey(self):

        survey = Survey.objects.create(
            user = self.user
        )
        survey.add_question("first question")

        self.assertEqual(len(survey.questions), 1)

        survey_question = SurveyQuestion.objects.get()
        self.assertEqual(survey_question.survey.id, survey.id)
        self.assertEqual(survey_question.label, "This is the first question")
        self.assertEqual(survey_question.answers.count(), 2)

    def testSurveyThrowsErrorIfQuestionDoesNotExist(self):
        survey = Survey.objects.create(
            user = self.user
        )

        try:
            survey.add_question("question does not exist")
            self.fail('Survey did not throw exception')
        except Survey.QuestionDoesNotExist:
            pass

    def testSurveySavesResponses(self):
        survey = Survey.objects.create(
            user = self.user
        )
        survey.add_question("first question")
        
        survey.save_response("first question", "first")

        survey_response = SurveyResponse.objects.get()
        self.assertEqual(survey_response.survey.id, survey.id)
        self.assertEqual(survey_response.question.name, "first question")
        self.assertEqual(survey_response.answer.value, "first")
    
    def testSurveySavesNullResponse(self):
        survey = Survey.objects.create(
            user = self.user
        )
        survey.add_question("first question")

        survey.save_response("first question", None)

        survey_response = SurveyResponse.objects.get()
        self.assertEqual(survey_response.survey.id, survey.id)
        self.assertEqual(survey_response.question.name, "first question")
        self.assertEqual(survey_response.answer, None)
