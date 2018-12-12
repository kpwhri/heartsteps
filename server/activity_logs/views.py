from datetime import datetime

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from fitbit_api.models import FitbitAccount, FitbitAccountUser, FitbitDay

from .serializers import FitbitDaySerializer
from .models import ActivityType

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def day_summary(request, day):
    try:
        account_user = FitbitAccountUser.objects.get(user=request.user)
        account = account_user.account
    except FitbitAccountUser.DoesNotExist:
        return Response('', status=status.HTTP_404_NOT_FOUND)   
    try:
        date = datetime.strptime(day, '%Y-%m-%d')
    except:
        return Response('', status=status.HTTP_400_BAD_REQUEST)
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
    try:   
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
    except:
        return Response('', status=status.HTTP_400_BAD_REQUEST)
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
