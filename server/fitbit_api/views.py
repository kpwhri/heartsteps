from datetime import datetime, timedelta
import pytz

from django.conf import settings
from django.utils import timezone
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from fitbit_api.services import FitbitClient, FitbitService, parse_fitbit_date
from fitbit_api.signals import update_date
from fitbit_api.models import FitbitAccount, FitbitUpdate, FitbitSubscription, FitbitSubscriptionUpdate

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def fitbit_account(request):
    try:
        service = FitbitService(user=request.user)
    except FitbitService.NoAccount:
        return Response({}, status=status.HTTP_404_NOT_FOUND)
    return Response({
        'fitbit': service.fitbit_user,
        'isAuthorized': service.is_authorized()
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def fitbit_subscription(request):
    if 'verify' in request.GET:
        if FitbitClient.verify_subscription_code(request.GET['verify']):
            return Response('', status=status.HTTP_204_NO_CONTENT)
        return Response('', status=status.HTTP_404_NOT_FOUND)
    
    fitbit_update = FitbitUpdate.objects.create(
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
                update = fitbit_update,
                payload = update
            ) 
            update_date.send(
                sender = FitbitAccount,
                fitbit_user = subscription.fitbit_account.fitbit_user,
                date = update['date']
            )
    return Response('', status=status.HTTP_204_NO_CONTENT)
