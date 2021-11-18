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
from fitbit_api.tasks import subscribe_to_fitbit
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from fitbit_authorize.models import AuthenticationSession

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
            session = AuthenticationSession.objects.get(
                token=token,
                disabled=False,
                created__gt=valid_time
            )
        except AuthenticationSession.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        fitbit = create_fitbit()
        callback_url = create_callback_url(request)
        authorize_url, state = fitbit.client.authorize_token_url(redirect_uri=callback_url)

        if 'redirect' in request.GET:
            session.redirect = request.GET['redirect']
        
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
           # print('KEYERROR in authorize_process on line 80 of fitbit_authorize/views')
            return redirect(reverse('fitbit-authorize-complete'))

        # TODO: delete hardcode for test-fitbit-patrick user
        # access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM0I3VlciLCJzdWIiOiI5SDRURDkiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJ3aHIgd251dCB3cHJvIHdzbGUgd3dlaSB3c29jIHdhY3Qgd3NldCB3bG9jIiwiZXhwIjoxNjI1NTUzNjM2LCJpYXQiOjE2MjU1MjQ4MzZ9.jWXetIEkygPszhLaPQOLrMaTiaH-647MjnbCydTktp8"
        # fitbit_user = '9H4TD9'
        # refresh_token = "34c416bd0fc6279063ec52a8a2360b03e1d039307b17f4e8c409f356a19f49bc"
        # expires_at = 1625553636.9566584

        fitbit_account, _ = FitbitAccount.objects.update_or_create(fitbit_user=fitbit_user, defaults={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        })
        try:
            FitbitAccountUser.objects.get(user=user, account=fitbit_account)
        except FitbitAccountUser.DoesNotExist:
            FitbitAccountUser.objects.create(
                account = fitbit_account,
                user = user
            )
        # TODO: re-enable async
        # x = subscribe_to_fitbit.apply_async(kwargs = {
        #     'username': fitbit_user
        # })

        print('before subscribe')
        subscription_result = subscribe_to_fitbit(username=fitbit_user)
        print('after subscribe')
        
        # TODO: remove print debugging
        # print('subscribe_to_fitbit non-async return value: ', subscription_result)
        # print('subscribe_to_fitbit async return value: ', subscription_result.get())

        if session.redirect:
            return redirect(session.redirect)
        return redirect(reverse('fitbit-authorize-complete'))
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def authorize_complete(request):
    return render(request, 'fitbit/index.html')
