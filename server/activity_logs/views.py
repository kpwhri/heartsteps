from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from fitbit_api.models import FitbitAccount, FitbitAccountUser, FitbitDay, FitbitActivity

from .serializers import ActivityLogSerializer, FitbitDaySerializer, FitbitActivitySerializer
from .models import ActivityLog, ActivityType

class ActivityLogsDetail(APIView):
    permissions_classes = (permissions.IsAuthenticated,)

    def get_activity(self, user, log_id):
        try:
            return ActivityLog.objects.get(
                user = user,
                uuid = log_id
            )
        except:
            raise Http404()
    
    def get(self, request, log_id):
        activity_log = self.get_activity(request.user, log_id)
        serialized = ActivityLogSerializer(activity_log)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, log_id):
        activity_log = self.get_activity(request.user, log_id)
        serialized = ActivityLogSerializer(data=request.data)
        if serialized.is_valid():
            activity_log.type = serialized.validated_data['type']
            activity_log.vigorous = serialized.validated_data['vigorous']
            activity_log.start = serialized.validated_data['start']
            activity_log.duration = serialized.validated_data['duration']
            activity_log.save()

            serialized_log = ActivityLogSerializer(activity_log)
            return Response(serialized_log.data, status=status.HTTP_200_OK)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, log_id):
        activity_log = self.get_activity(request.user, log_id)
        activity_log.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ActivityLogsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serialized = ActivityLogSerializer(data=request.data)
        if serialized.is_valid():
            activity_log = ActivityLog(**serialized.validated_data)
            activity_log.user = request.user
            activity_log.save()
            serialzied_log = ActivityLogSerializer(activity_log)
            return Response(serialzied_log.data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


def get_fitbit_account(user):
    try:
        account_user = FitbitAccountUser.objects.get(user=user)
        return account_user.account
    except FitbitAccountUser.DoesNotExist:
        raise Http404

def parse_date(day):
    try:
        return datetime.strptime(day, '%Y-%m-%d')
    except:
        raise Http404


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def day_summary(request, day):
    account = get_fitbit_account(request.user)
    date = parse_date(day)
    try:
        results = FitbitDay.objects.get(
            account = account,
            date__year=date.year,
            date__month=date.month,
            date__day=date.day
        )
        serialized = FitbitDaySerializer(results)
        return Response(serialized.data, status=status.HTTP_200_OK)
    except FitbitDay.DoesNotExist:
        return Response('', status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def date_range_summary(request, start, end):
    try:
        account_user = FitbitAccountUser.objects.get(user=request.user)
        account = account_user.account
    except FitbitAccountUser.DoesNotExist:
        return Response('', status=status.HTTP_404_NOT_FOUND)
    start_date = parse_date(start)
    end_date = parse_date(end)
    try:
        results = FitbitDay.objects.filter(
            account = account,
            date__year__gte=start_date.year,
            date__month__gte=start_date.month,
            date__day__gte=start_date.day,
            date__year__lte=end_date.year,
            date__month__lte=end_date.month,
            date__day__lte=end_date.day
        ).order_by('date').all()
        serialized = FitbitDaySerializer(results, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    except:
        return Response('', status=status.HTTP_404_NOT_FOUND)
