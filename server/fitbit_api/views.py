from datetime import timedelta

from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from fitbit_api.services import create_fitbit, create_callback_url, FitbitClient
from fitbit_api.tasks import subscribe_to_fitbit, update_fitbit_data
from fitbit_api.models import FitbitAccount, FitbitSubscription, FitbitSubscriptionUpdate, AuthenticationSession

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
    subscriptions_to_update = []
    for update in request.data:
        if 'subscriptionId' in update:
            try:
                subscription = FitbitSubscription.objects.get(uuid=update['subscriptionId'])
            except FitbitSubscription.DoesNotExist:
                continue
            if subscription not in subscriptions_to_update:
                subscriptions_to_update.append(subscription)
            FitbitSubscriptionUpdate.objects.create(
                subscription = subscription,
                payload = update
            )
    for subscription in subscriptions_to_update:
        update_fitbit_data.apply_async(kwargs={
            'username': subscription.fitbit_account.user.username
        }
        )
    return Response('', status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def authorize_start(request):
    AuthenticationSession.objects.filter(user=request.user, disabled=False).update(disabled=True)
    session = AuthenticationSession.objects.create(user=request.user)
    return Response({
        'token': str(session.token)
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def authorize(request, token):
    if token:
        try:
            valid_time = timezone.now() - timedelta(hours=1)
            session = AuthenticationSession.objects.get(token=token, disabled=False, created__gt=valid_time)
        except AuthenticationSession.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        fitbit = create_fitbit()
        callback_url = create_callback_url(request)
        authorize_url, state = fitbit.client.authorize_token_url(redirect_uri=callback_url)
        
        session.state = state
        session.save()

        return redirect(authorize_url)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def authorize_process(request):
    if 'code' in request.GET and 'state' in request.GET:
        try:
            valid_time = timezone.now() - timedelta(hours=1)
            session = AuthenticationSession.objects.get(
                state=request.GET['state'],
                disabled=False,
                created__gt=valid_time
                )
            user = session.user
        except AuthenticationSession.DoesNotExist:
            return redirect(reverse('fitbit-authorize-complete'))

        session.disabled = True
        session.save()

        code = request.GET['code']
        fitbit = create_fitbit()
        try:
            callback_url = create_callback_url(request)
            token = fitbit.client.fetch_access_token(code, redirect_uri=callback_url)
            access_token = token['access_token']
            fitbit_user = token['user_id']
            refresh_token = token['refresh_token']
            expires_at = token['expires_at']
        except KeyError:
            return redirect(reverse('fitbit-authorize-complete'))

        fitbit_account, _ = FitbitAccount.objects.update_or_create(user=user, defaults={
            'fitbit_user': fitbit_user,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        })
        subscribe_to_fitbit.apply_async(kwargs = {
            'username': user.username
        })
        
        return redirect(reverse('fitbit-authorize-complete'))
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def authorize_complete(request):
    return render(request, 'fitbit/index.html')
