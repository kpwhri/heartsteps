from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from fitapp.utils import create_fitbit

from push_messages.functions import send_notification

from fitbit_api.models import FitbitAccount


@api_view(['GET'])
def authorize(request, username):
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        login(request, user)

        complete_url = request.build_absolute_uri(reverse('fitbit-authorize-process'))
        if not settings.DEBUG and 'https://' not in complete_url:
            complete_url = complete_url.replace('http://', 'https://')

        fitbit = create_fitbit()
        authorize_url, security_token = fitbit.client.authorize_token_url(redirect_uri=complete_url)
        
        return redirect(authorize_url)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def authorize_process(request):
    user = request.user

    if 'code' in request.GET['code']:
        code = request.GET['code']
        fitbit = create_fitbit()
        try:
            token = fitbit.client.fetch_access_token(code)
            access_token = token['access_token']
            fitbit_user = token['user_id']
        except KeyError:
            send_notification(request.user, 'HeartSteps Fit Authentication', 'There was a problem authenticating with you FitBit account', data={
                'fitbit_id': None
            })
            return redirect(reverse('fitbit-authorize-complete'))
        
        fitbit_account, _ = FitbitAccount.objects.update_or_create(user=user, defaults={
            'fitbit_user': fitbit_user,
            'access_token': access_token,
            'refresh_token': token['refresh_token'],
            'expires_at': token['expires_at']
        })

        send_notification(user, 'HeartSteps Fit Authentication', 'Your FitBit account has been authenticated', data={
            'fitbit_id': fitbit_account.fitbit_user
        })
        return redirect(reverse('fitbit-authorize-complete'))
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def authorize_complete(request):
    return render(request, 'fitbit/index.html', {
        authorized: True
    })
