from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from datetime import timedelta
from participants.models import Participant
from django.http.response import Http404

from dashboard.models import DashboardParticipant
from surveys.models import Survey
from surveys.serializers import SurveyExpander
from .models import Message, Device, MessageReceipt
from .serializers import DeviceSerializer, MessageReceiptSerializer, MessageSerializer

from django.utils import timezone
from user_event_logs.models import EventLog
import json

class DeviceView(APIView):
    """
    Manage a user's Firebase Cloud Messaging Device
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            device = Device.objects.get(user=request.user, active=True)
        except Device.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        serialized_device = DeviceSerializer(device)
        return Response(serialized_device.data, status=status.HTTP_200_OK)

    def post(self, request):
        serialized_device = DeviceSerializer(data=request.data, context={
            'user': request.user
        })
        if serialized_device.is_valid():
            Device.objects.filter(
                user=request.user, active=True).update(active=False)

            Device.objects.create(
                user=request.user,
                token=serialized_device.validated_data['token'],
                type=serialized_device.validated_data['type'],
                active=True
            )

            curr_device = Device.objects.get(user=request.user, active=True)
            user_token = curr_device.token
            devices_with_token = Device.objects.filter(token=user_token, active=True)
            for device in devices_with_token:
                if device.user != request.user:
                    # print("id: {}, user: {}, token: {}, created: {}, active: {}" \
                    #     .format(device.id, device.user, device.token, device.created, device.active))
                    device.active = False
                    device.save()
            
            return Response(serialized_device.data, status=status.HTTP_201_CREATED)

        return Response({}, status=status.HTTP_400_BAD_REQUEST)


class MessageView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, message_id):
        try:
            EventLog.debug(request.user, "MessageView.get(): {}".format(message_id))
            message = Message.objects.get(
                uuid=message_id
            )
            EventLog.debug(request.user, "MessageView.get(): {}".format(message))
            # try expanding the survey message
            try:
                context = message.data
                EventLog.debug(request.user, "MessageView.get(): {}".format(context))
                if "survey" in context:
                    survey_json = context["survey"]
                    survey_payload = json.loads(survey_json)
                    survey_uuid = survey_payload["id"]
                    
                    survey_query = Survey.objects.filter(uuid=survey_uuid)
                    
                    if survey_query.exists():
                        se = SurveyExpander(survey_uuid)
                        EventLog.debug(request.user, "MessageView.get(): {}".format(se))
                        message.data["survey"] = se.to_json()
                        EventLog.debug(request.user, "MessageView.get(): {}".format(message.data))
                    else:
                        # this uuid is not from Survey
                        EventLog.debug(request.user, "The uuid is not found in survey table: {}".format(survey_uuid))
                else:
                    # this uuid is not from Survey
                    EventLog.debug(request.user, "There is no 'survey' key in the message context: {}".format(context))
            except Exception as e:
                EventLog.debug(request.user, "Something happened during message expansion: {}".format(e))
                    
            EventLog.debug(request.user, "MessageView.get(): {}".format(message))
        except Message.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        EventLog.debug(request.user, "MessageView.get(): {}".format(message))
        if request.user.id != message.recipient.id:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(
            {
                'id': str(message.uuid),
                'type': message.message_type,
                'title': message.title,
                'body': message.body,
                'context': message.data
            },
            status=status.HTTP_200_OK
        )


class RecievedMessageView(APIView):
    """
    Checks if the message_id that was sent matches the current user, and of so
    marks the message as recieved with the current datetime.

    If the message has already been recieved, the recieved datetime is not
    udpated.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def create_message_receipt(self, message, receipt_type, time):
        try:
            MessageReceipt.objects.get(
                message=message,
                type=receipt_type
            )
        except MessageReceipt.DoesNotExist:
            MessageReceipt.objects.create(
                message=message,
                type=receipt_type,
                time=time
            )

    def post(self, request):
        serialized_receipts = MessageReceiptSerializer(data=request.data, context={
            'user': request.user
        }, many=True)
        if serialized_receipts.is_valid():
            for serialized_receipt in serialized_receipts.validated_data:
                for receipt_type in MessageReceipt.MESSAGE_RECEIPT_TYPES:
                    if receipt_type in serialized_receipt:
                        self.create_message_receipt(
                            serialized_receipt['message'],
                            receipt_type,
                            serialized_receipt[receipt_type]
                        )
            return Response({}, status.HTTP_200_OK)
        return Response(serialized_receipts.errors, status.HTTP_400_BAD_REQUEST)


class ParticipantNotificationEndpointView(APIView):
    permissions_classes = (permissions.IsAuthenticated,)

    def setup_participant(self, participant_id_setup):
        if participant_id_setup is not None:
            try:
                participant = DashboardParticipant.objects.get(
                    heartsteps_id=participant_id_setup)
                return participant
            except Participant.DoesNotExist:
                raise Http404('No matching participant')
        else:
            raise Http404('No participant')

    def get_notifications(self, user, start, end):
        if not user:
            return []
        notifications = Message.objects.filter(
            recipient=user,
            message_type=Message.NOTIFICATION,
            created__gte=start,
            created__lte=end
        ) \
            .order_by('-created') \
            .localize_datetimes() \
            .all()
        return notifications

    def is_received(self, notification):
        if notification.sent and notification.received:
            return True
        return False

    def is_read(self, notification):
        if self.is_received(notification):
            if notification.engaged or notification.opened:
                return True
        return False

    def are_unread_notifications(self, notifications):
        if notifications:
            for notification in notifications:
                if self.is_received(notification) and not self.is_read(notification):
                    return True
        return False

    def get(self, request):
        start = timezone.now() - timedelta(days=1)
        end = timezone.now()

        # check to see if the request is allowed (i.e. participant is logged in)
        if request.user.is_anonymous:
            raise Http404('No participant, please log in')

        # check to see if the participant exists
        self.setup_participant(request.user)

        notifications = self.get_notifications(request.user, start, end)
        are_unread = self.are_unread_notifications(notifications)
        serialized = MessageSerializer(notifications, many=True)
        return Response([are_unread, serialized.data], status=status.HTTP_200_OK)
