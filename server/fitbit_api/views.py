from datetime import datetime, timedelta
import pytz

from django.conf import settings
from django.utils import timezone
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from fitbit_api.services import FitbitClient
from fitbit_api.tasks import update_fitbit_data
from fitbit_api.models import FitbitAccount, FitbitUpdate, FitbitSubscription, FitbitSubscriptionUpdate, FitbitDay
from fitbit_api.serializers import FitbitDaySerializer

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def fitbit_account(request):
    try:
        account = FitbitAccount.objects.get(user=request.user)
    except FitbitAccount.DoesNotExist:
        return Response({}, status=status.HTTP_404_NOT_FOUND)
    return Response({
        'fitbit': account.fitbit_user
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def fitbit_subscription(request):
    if 'verify' in request.GET:
        if FitbitClient.verify_subscription_code(request.GET['verify']):
            return Response('', status=status.HTTP_204_NO_CONTENT)
        return Response('', status=status.HTTP_404_NOT_FOUND)
    
    FitbitUpdate.objects.create(
        payload = request.data
    )
    for update in request.data:
        if 'subscriptionId' in update:
            try:
                subscription = FitbitSubscription.objects.get(uuid=update['subscriptionId'])
            except FitbitSubscription.DoesNotExist:
                continue
            FitbitSubscriptionUpdate.objects.create(
                subscription = subscription,
                payload = update
            )
            update_fitbit_data.apply_async(kwargs={
                'username': subscription.fitbit_account.user.username,
                'date_string': update['date']
            })        
    return Response('', status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def fitbit_day_logs(request, day):
    try:
        account = FitbitAccount.objects.get(user=request.user)
    except FitbitAccount.DoesNotExist:
        return Response('', status=status.HTTP_404_NOT_FOUND)    
    
    try:
        date = datetime.strptime(day, '%Y-%m-%d')
        results = FitbitDay.objects.get(
            account = account,
            date__year=date.year,
            date__month=date.month,
            date__day=date.day
        )
        serialized = FitbitDaySerializer(results)
        return Response(serialized.data, status=status.HTTP_200_OK)
    except:
        return Response('', status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def fitbit_date_range_logs(request, start, end):
    try:
        account = FitbitAccount.objects.get(user=request.user)
    except FitbitAccount.DoesNotExist:
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
