import pytz
from datetime import datetime, date

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from locations.services import LocationService
from days.views import DayView

from .services import MorningMessageService
from .serializers import MorningMessageSerializer, MorningMessageSurveySerializer


class AnchorMessageView(DayView):
    permission_classes = [IsAuthenticated]

    def get(self, request, day):
        date = self.parse_date(day)
        self.validate_date(request.user, date)
        morning_message_service = MorningMessageService(
            user=request.user
        )
        morning_message, _ = morning_message_service.get_or_create(date)
        return Response({
            'message': morning_message.anchor
        }, status=status.HTTP_200_OK)


class MorningMessageView(DayView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, day):
        date = self.parse_date(day)
        self.validate_date(request.user, date)
        morning_message_service = MorningMessageService(
            user=request.user
        )
        morning_message, _ = morning_message_service.get_or_create(date)
        serialized = MorningMessageSerializer(morning_message)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, day):
        date = self.parse_date(day)
        self.validate_date(request.user, date)
        morning_message_service = MorningMessageService(user=request.user)
        notification = morning_message_service.send_notification(date)
        return Response({
            'notificationId': str(notification.uuid)
        }, status=status.HTTP_201_CREATED)


class MorningMessageSurveyView(DayView):

    def get_survey(self, request, day):
        date = self.parse_date(day)
        self.validate_date(request.user, date)
        morning_message_service = MorningMessageService(
            user=request.user
        )
        morning_message, _ = morning_message_service.get_or_create(date)
        if morning_message.survey:
            return morning_message.survey
        else:
            raise Http404()

    def get(self, request, day):
        survey = self.get_survey(request, day)
        serialized = MorningMessageSurveySerializer(survey)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, day):
        survey = self.get_survey(request, day)

        for key in request.data:
            if key == 'selected_word':
                selected_word = request.data['selected_word']
                if selected_word in survey.word_set:
                    survey.selected_word = request.data['selected_word']
                    # survey.answered = True
                    survey.save()
            else:
                survey.save_response(key, request.data[key])

        return Response(survey.get_answers(), status=status.HTTP_200_OK)


class MorningMessageSurveyResponseView(MorningMessageSurveyView):

    def get(self, request, day):
        survey = self.get_survey(request, day)
        return Response(survey.get_answers(), status=status.HTTP_200_OK)
