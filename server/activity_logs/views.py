from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from fitbit_api.models import FitbitAccount, FitbitAccountUser, FitbitDay, FitbitActivity

from .serializers import FitbitDaySerializer, FitbitActivitySerializer
from .models import ActivityType

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
def activities(request, day):
    account = get_fitbit_account(request.user)
    date = parse_date(day)
    try:
        fitbit_day = FitbitDay.objects.get(
            account=account,
            date__year=date.year,
            date__month = date.month,
            date__day = date.day
        )
        activities = FitbitActivity.objects.filter(day=fitbit_day).all()
        serialized = FitbitActivitySerializer(activities, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    except FitbitDay.DoesNotExist:
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
